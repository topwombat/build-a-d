"""pyCycle afterburning turbojet used to generate the engine deck.

Adapted from pyCycle's ``example_cycles/afterburning_turbojet.py``
(Apache-2.0, https://github.com/OpenMDAO/pyCycle). Single-spool turbojet with
an afterburner and a convergent-divergent nozzle, tabular Jet-A thermo.

Cycle variables exposed to the optimizer (brief: "three or four"):
    opr        compressor pressure ratio at the design point
    t4_max_K   burner exit (turbine inlet) total temperature limit
    fn_sls_kN  dry sea-level static thrust at the design point (sets airflow)
    t_ab_K     afterburner exit total temperature at full reheat
"""
from __future__ import annotations

import numpy as np
import openmdao.api as om
import pycycle.api as pyc


class ABTurbojet(pyc.Cycle):
    def setup(self):
        self.options["thermo_method"] = "TABULAR"
        self.options["thermo_data"] = pyc.AIR_JETA_TAB_SPEC
        fuel = "FAR"
        design = self.options["design"]

        self.add_subsystem("fc", pyc.FlightConditions())
        self.add_subsystem("inlet", pyc.Inlet())
        self.add_subsystem("duct1", pyc.Duct())
        self.add_subsystem(
            "comp",
            pyc.Compressor(map_data=pyc.AXI5, bleed_names=["cool1", "cool2"], map_extrap=True),
            promotes_inputs=["Nmech"],
        )
        self.add_subsystem("burner", pyc.Combustor(fuel_type=fuel))
        self.add_subsystem(
            "turb",
            pyc.Turbine(map_data=pyc.LPT2269, bleed_names=["cool1", "cool2"], map_extrap=True),
            promotes_inputs=["Nmech"],
        )
        self.add_subsystem("ab", pyc.Combustor(fuel_type=fuel))
        self.add_subsystem("nozz", pyc.Nozzle(nozzType="CD", lossCoef="Cv", internal_solver=True))
        self.add_subsystem("shaft", pyc.Shaft(num_ports=2), promotes_inputs=["Nmech"])
        self.add_subsystem("perf", pyc.Performance(num_nozzles=1, num_burners=2))

        self.connect("duct1.Fl_O:tot:P", "perf.Pt2")
        self.connect("comp.Fl_O:tot:P", "perf.Pt3")
        self.connect("burner.Wfuel", "perf.Wfuel_0")
        self.connect("ab.Wfuel", "perf.Wfuel_1")
        self.connect("inlet.F_ram", "perf.ram_drag")
        self.connect("nozz.Fg", "perf.Fg_0")
        self.connect("comp.trq", "shaft.trq_0")
        self.connect("turb.trq", "shaft.trq_1")
        self.connect("fc.Fl_O:stat:P", "nozz.Ps_exhaust")

        balance = self.add_subsystem("balance", om.BalanceComp())
        if design:
            balance.add_balance("W", units="lbm/s", eq_units="lbf")
            self.connect("balance.W", "inlet.Fl_I:stat:W")
            self.connect("perf.Fn", "balance.lhs:W")

            balance.add_balance("FAR", eq_units="degR", lower=1e-4, val=0.017)
            self.connect("balance.FAR", "burner.Fl_I:FAR")
            self.connect("burner.Fl_O:tot:T", "balance.lhs:FAR")

            balance.add_balance("turb_PR", val=1.5, lower=1.001, upper=12, eq_units="hp", rhs_val=0.0)
            self.connect("balance.turb_PR", "turb.PR")
            self.connect("shaft.pwr_net", "balance.lhs:turb_PR")
        else:
            balance.add_balance("FAR", eq_units="degR", lower=1e-4, val=0.017)
            self.connect("balance.FAR", "burner.Fl_I:FAR")
            self.connect("burner.Fl_O:tot:T", "balance.lhs:FAR")

            balance.add_balance("Nmech", val=8000.0, units="rpm", lower=500.0, upper=14000.0,
                                eq_units="hp", use_mult=True, mult_val=-1)
            self.connect("balance.Nmech", "Nmech")
            self.connect("shaft.pwr_in", "balance.lhs:Nmech")
            self.connect("shaft.pwr_out", "balance.rhs:Nmech")

            balance.add_balance("W", val=100.0, units="lbm/s", eq_units=None, rhs_val=2.0)
            self.connect("balance.W", "inlet.Fl_I:stat:W")
            self.connect("comp.map.RlineMap", "balance.lhs:W")

        self.set_order(["fc", "inlet", "duct1", "comp", "burner", "turb", "ab", "nozz",
                        "shaft", "perf", "balance"])

        self.pyc_connect_flow("fc.Fl_O", "inlet.Fl_I", connect_w=False)
        self.pyc_connect_flow("inlet.Fl_O", "duct1.Fl_I", connect_stat=False)
        self.pyc_connect_flow("duct1.Fl_O", "comp.Fl_I", connect_stat=False)
        self.pyc_connect_flow("comp.Fl_O", "burner.Fl_I", connect_stat=False)
        self.pyc_connect_flow("burner.Fl_O", "turb.Fl_I", connect_stat=False)
        self.pyc_connect_flow("turb.Fl_O", "ab.Fl_I", connect_stat=False)
        self.pyc_connect_flow("ab.Fl_O", "nozz.Fl_I", connect_stat=False)
        self.pyc_connect_flow("comp.cool1", "turb.cool1", connect_stat=False)
        self.pyc_connect_flow("comp.cool2", "turb.cool2", connect_stat=False)

        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options["atol"] = 1e-6
        newton.options["rtol"] = 1e-6
        newton.options["iprint"] = -1
        newton.options["maxiter"] = 30
        newton.options["solve_subsystems"] = True
        newton.options["max_sub_solves"] = 100
        newton.options["reraise_child_analysiserror"] = False
        newton.linesearch = om.ArmijoGoldsteinLS()
        newton.linesearch.options["rho"] = 0.75
        newton.linesearch.options["iprint"] = -1
        self.linear_solver = om.DirectSolver()
        super().setup()


class DesignPlusOffDesign(pyc.MPCycle):
    """One design point plus one off-design point that is re-run across the deck grid.

    Full reheat is solved outside the Newton loop by a secant iteration on the
    afterburner fuel-air ratio (see deck.py); a balance inside the cycle diverged.
    """

    def setup(self):
        self.pyc_add_pnt("DESIGN", ABTurbojet(design=True))
        self.set_input_defaults("DESIGN.Nmech", 8070.0, units="rpm")
        self.set_input_defaults("DESIGN.inlet.MN", 0.60)
        self.set_input_defaults("DESIGN.duct1.MN", 0.60)
        self.set_input_defaults("DESIGN.comp.MN", 0.20)
        self.set_input_defaults("DESIGN.burner.MN", 0.20)
        self.set_input_defaults("DESIGN.turb.MN", 0.4)
        self.set_input_defaults("DESIGN.ab.MN", 0.4)
        self.set_input_defaults("DESIGN.ab.Fl_I:FAR", 0.000)

        self.pyc_add_cycle_param("duct1.dPqP", 0.02)
        self.pyc_add_cycle_param("burner.dPqP", 0.03)
        self.pyc_add_cycle_param("ab.dPqP", 0.06)
        self.pyc_add_cycle_param("nozz.Cv", 0.99)
        self.pyc_add_cycle_param("comp.cool1:frac_W", 0.0789)
        self.pyc_add_cycle_param("comp.cool1:frac_P", 1.0)
        self.pyc_add_cycle_param("comp.cool1:frac_work", 1.0)
        self.pyc_add_cycle_param("comp.cool2:frac_W", 0.0383)
        self.pyc_add_cycle_param("comp.cool2:frac_P", 1.0)
        self.pyc_add_cycle_param("comp.cool2:frac_work", 1.0)
        self.pyc_add_cycle_param("turb.cool1:frac_P", 1.0)
        self.pyc_add_cycle_param("turb.cool2:frac_P", 0.0)

        self.pyc_add_pnt("OD", ABTurbojet(design=False))
        self.set_input_defaults("OD.fc.MN", val=0.5)
        self.set_input_defaults("OD.fc.alt", val=0.0, units="ft")
        self.set_input_defaults("OD.balance.rhs:FAR", val=2370.0, units="degR")
        self.set_input_defaults("OD.balance.rhs:W", val=2.0)
        self.set_input_defaults("OD.ab.Fl_I:FAR", val=0.0)

        for a, b in [("comp.s_PR",) * 2, ("comp.s_Wc",) * 2, ("comp.s_eff",) * 2, ("comp.s_Nc",) * 2,
                     ("turb.s_PR",) * 2, ("turb.s_Wp",) * 2, ("turb.s_eff",) * 2, ("turb.s_Np",) * 2,
                     ("inlet.Fl_O:stat:area", "inlet.area"), ("duct1.Fl_O:stat:area", "duct1.area"),
                     ("comp.Fl_O:stat:area", "comp.area"), ("burner.Fl_O:stat:area", "burner.area"),
                     ("turb.Fl_O:stat:area", "turb.area"), ("ab.Fl_O:stat:area", "ab.area")]:
            self.pyc_connect_des_od(a, b)
        super().setup()
