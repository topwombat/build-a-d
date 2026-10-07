"""Two-spool gas-turbine cycles in pyCycle: afterburning turbojet and mixed-flow turbofan.

One cycle class covers both architectures (D-024):

``bypass=False``  LP compressor + HP compressor, HP and LP turbines, optional afterburner,
                  CD nozzle. Used for the Concorde/Olympus 593 validation engine.
``bypass=True``   fan + core (HP compressor, burner, HP turbine) + LP turbine, forced mixer,
                  optional afterburner, CD nozzle. The core is the bought gas generator; the
                  fan, LP turbine, mixer and nozzle are ours.

Off-design, dry operation holds the nozzle throat at its design area; with reheat the nozzle
opens to hold the LP compressor (fan) on the dry operating line, so reheat does not re-match the
gas generator (``wctl`` selector, s = 0 dry / s = 1 reheat).
Adapted from pyCycle's ``mixedflow_turbofan.py`` and ``afterburning_turbojet.py`` examples
(Apache-2.0). Component maps: pyCycle FanMap / LPCMap / HPCMap / HPTMap / LPTMap.
"""
from __future__ import annotations

import openmdao.api as om
import pycycle.api as pyc

FUEL = "FAR"


class TwoSpool(pyc.Cycle):
    def initialize(self):
        self.options.declare("bypass", default=False)
        self.options.declare("afterburner", default=True)
        super().initialize()

    def setup(self):
        self.options["thermo_method"] = "TABULAR"
        self.options["thermo_data"] = pyc.AIR_JETA_TAB_SPEC
        design = self.options["design"]
        byp = self.options["bypass"]
        ab = self.options["afterburner"]

        self.add_subsystem("fc", pyc.FlightConditions())
        self.add_subsystem("inlet", pyc.Inlet())
        lp_map = pyc.FanMap if byp else pyc.LPCMap
        self.add_subsystem("lpc", pyc.Compressor(map_data=lp_map, map_extrap=True),
                           promotes_inputs=[("Nmech", "LP_Nmech")])
        if byp:
            self.add_subsystem("splitter", pyc.Splitter())
            self.add_subsystem("bypass_duct", pyc.Duct())
        self.add_subsystem("hpc", pyc.Compressor(map_data=pyc.HPCMap, map_extrap=True,
                                                 bleed_names=["cool_hpt", "cool_lpt"]),
                           promotes_inputs=[("Nmech", "HP_Nmech")])
        self.add_subsystem("burner", pyc.Combustor(fuel_type=FUEL))
        self.add_subsystem("hpt", pyc.Turbine(map_data=pyc.HPTMap, map_extrap=True, bleed_names=["cool_hpt"]),
                           promotes_inputs=[("Nmech", "HP_Nmech")])
        self.add_subsystem("lpt", pyc.Turbine(map_data=pyc.LPTMap, map_extrap=True, bleed_names=["cool_lpt"]),
                           promotes_inputs=[("Nmech", "LP_Nmech")])
        if byp:
            self.add_subsystem("mixer", pyc.Mixer(designed_stream=1))
        if ab:
            self.add_subsystem("ab", pyc.Combustor(fuel_type=FUEL))
        self.add_subsystem("nozz", pyc.Nozzle(nozzType="CD", lossCoef="Cv", internal_solver=True))
        self.add_subsystem("lp_shaft", pyc.Shaft(num_ports=2), promotes_inputs=[("Nmech", "LP_Nmech")])
        self.add_subsystem("hp_shaft", pyc.Shaft(num_ports=2), promotes_inputs=[("Nmech", "HP_Nmech")])
        self.add_subsystem("perf", pyc.Performance(num_nozzles=1, num_burners=2 if ab else 1))

        # flow path
        self.pyc_connect_flow("fc.Fl_O", "inlet.Fl_I", connect_w=False)
        self.pyc_connect_flow("inlet.Fl_O", "lpc.Fl_I", connect_stat=False)
        if byp:
            self.pyc_connect_flow("lpc.Fl_O", "splitter.Fl_I", connect_stat=False)
            self.pyc_connect_flow("splitter.Fl_O1", "hpc.Fl_I", connect_stat=False)
            self.pyc_connect_flow("splitter.Fl_O2", "bypass_duct.Fl_I", connect_stat=False)
        else:
            self.pyc_connect_flow("lpc.Fl_O", "hpc.Fl_I", connect_stat=False)
        self.pyc_connect_flow("hpc.Fl_O", "burner.Fl_I", connect_stat=False)
        self.pyc_connect_flow("burner.Fl_O", "hpt.Fl_I", connect_stat=False)
        self.pyc_connect_flow("hpt.Fl_O", "lpt.Fl_I", connect_stat=False)
        last = "lpt.Fl_O"
        if byp:
            self.pyc_connect_flow("lpt.Fl_O", "mixer.Fl_I1")
            self.pyc_connect_flow("bypass_duct.Fl_O", "mixer.Fl_I2")
            last = "mixer.Fl_O"
        if ab:
            self.pyc_connect_flow(last, "ab.Fl_I", connect_stat=False)
            last = "ab.Fl_O"
        self.pyc_connect_flow(last, "nozz.Fl_I", connect_stat=False)
        self.pyc_connect_flow("hpc.cool_hpt", "hpt.cool_hpt", connect_stat=False)
        self.pyc_connect_flow("hpc.cool_lpt", "lpt.cool_lpt", connect_stat=False)

        self.connect("inlet.Fl_O:tot:P", "perf.Pt2")
        self.connect("hpc.Fl_O:tot:P", "perf.Pt3")
        self.connect("burner.Wfuel", "perf.Wfuel_0")
        if ab:
            self.connect("ab.Wfuel", "perf.Wfuel_1")
        self.connect("inlet.F_ram", "perf.ram_drag")
        self.connect("nozz.Fg", "perf.Fg_0")
        self.connect("lpc.trq", "lp_shaft.trq_0")
        self.connect("lpt.trq", "lp_shaft.trq_1")
        self.connect("hpc.trq", "hp_shaft.trq_0")
        self.connect("hpt.trq", "hp_shaft.trq_1")
        self.connect("fc.Fl_O:stat:P", "nozz.Ps_exhaust")

        bal = self.add_subsystem("balance", om.BalanceComp())
        bal.add_balance("FAR", eq_units="degR", lower=1e-4, upper=0.06, val=0.02)
        self.connect("balance.FAR", "burner.Fl_I:FAR")
        self.connect("burner.Fl_O:tot:T", "balance.lhs:FAR")
        if design:
            bal.add_balance("W", units="lbm/s", eq_units="lbf", lower=1.0, upper=2000.0)
            self.connect("balance.W", "inlet.Fl_I:stat:W")
            self.connect("perf.Fn", "balance.lhs:W")
            bal.add_balance("hpt_PR", val=3.0, lower=1.001, upper=12, eq_units="hp", use_mult=True, mult_val=-1)
            self.connect("balance.hpt_PR", "hpt.PR")
            self.connect("hp_shaft.pwr_in", "balance.lhs:hpt_PR")
            self.connect("hp_shaft.pwr_out", "balance.rhs:hpt_PR")
            bal.add_balance("lpt_PR", val=2.0, lower=1.001, upper=12, eq_units="hp", use_mult=True, mult_val=-1)
            self.connect("balance.lpt_PR", "lpt.PR")
            self.connect("lp_shaft.pwr_in", "balance.lhs:lpt_PR")
            self.connect("lp_shaft.pwr_out", "balance.rhs:lpt_PR")
            if byp:
                # BPR follows from the mixer: core and bypass total pressures in the design ratio
                bal.add_balance("BPR", eq_units=None, lower=0.1, upper=8.0, val=1.0)
                self.connect("balance.BPR", "splitter.BPR")
                self.connect("mixer.ER", "balance.lhs:BPR")
        else:
            # Airflow control: s = 0 holds the nozzle throat at its design area (dry operation);
            # s = 1 holds the LP compressor / fan on a given operating line (reheat: the nozzle opens
            # so the gas generator keeps its dry match).
            self.add_subsystem("wctl", om.ExecComp(
                ["y = s*rline + (1.0 - s)*area/a_ref", "y_tgt = s*rline_tgt + (1.0 - s)"],
                area={"units": "inch**2", "val": 500.0}, a_ref={"units": "inch**2", "val": 500.0},
                rline={"val": 2.0}, rline_tgt={"val": 2.0}, s={"val": 0.0}))
            self.connect("nozz.Throat:stat:area", "wctl.area")
            self.connect("lpc.map.RlineMap", "wctl.rline")
            bal.add_balance("W", units="lbm/s", eq_units=None, lower=1.0, upper=2000.0, val=100.0)
            self.connect("balance.W", "inlet.Fl_I:stat:W")
            self.connect("wctl.y", "balance.lhs:W")
            self.connect("wctl.y_tgt", "balance.rhs:W")
            bal.add_balance("LP_Nmech", val=4000.0, units="rpm", lower=200.0, eq_units="hp",
                            use_mult=True, mult_val=-1)
            self.connect("balance.LP_Nmech", "LP_Nmech")
            self.connect("lp_shaft.pwr_in", "balance.lhs:LP_Nmech")
            self.connect("lp_shaft.pwr_out", "balance.rhs:LP_Nmech")
            bal.add_balance("HP_Nmech", val=12000.0, units="rpm", lower=500.0, eq_units="hp",
                            use_mult=True, mult_val=-1)
            self.connect("balance.HP_Nmech", "HP_Nmech")
            self.connect("hp_shaft.pwr_in", "balance.lhs:HP_Nmech")
            self.connect("hp_shaft.pwr_out", "balance.rhs:HP_Nmech")
            if byp:
                bal.add_balance("BPR", lower=0.1, upper=8.0, eq_units="psi", val=1.0)
                self.connect("balance.BPR", "splitter.BPR")
                self.connect("mixer.Fl_I1_calc:stat:P", "balance.lhs:BPR")
                self.connect("bypass_duct.Fl_O:stat:P", "balance.rhs:BPR")

        order = ["fc", "inlet", "lpc"] + (["splitter", "bypass_duct"] if byp else []) + [
            "hpc", "burner", "hpt", "lpt"] + (["mixer"] if byp else []) + (["ab"] if ab else []) + [
            "nozz", "lp_shaft", "hp_shaft", "perf"] + ([] if design else ["wctl"]) + ["balance"]
        self.set_order(order)

        newton = self.nonlinear_solver = om.NewtonSolver()
        for k, v in dict(atol=1e-6, rtol=1e-6, iprint=-1, maxiter=40, solve_subsystems=True,
                         max_sub_solves=100, reraise_child_analysiserror=False).items():
            newton.options[k] = v
        newton.linesearch = om.ArmijoGoldsteinLS()
        newton.linesearch.options["rho"] = 0.75
        newton.linesearch.options["iprint"] = -1
        self.linear_solver = om.DirectSolver()
        super().setup()


class DesignAndOffDesign(pyc.MPCycle):
    def initialize(self):
        self.options.declare("bypass", default=False)
        self.options.declare("afterburner", default=True)
        super().initialize()

    def setup(self):
        byp, ab = self.options["bypass"], self.options["afterburner"]
        self.pyc_add_pnt("DESIGN", TwoSpool(design=True, bypass=byp, afterburner=ab))
        mns = {"inlet.MN": 0.6, "lpc.MN": 0.45, "hpc.MN": 0.25, "burner.MN": 0.10, "hpt.MN": 0.35,
               "lpt.MN": 0.40, "nozz.Cv": None}
        if byp:
            mns |= {"splitter.MN1": 0.30, "splitter.MN2": 0.45, "bypass_duct.MN": 0.45}
        if ab:
            mns |= {"ab.MN": 0.20}
        for k, v in mns.items():
            if v is not None:
                self.set_input_defaults(f"DESIGN.{k}", v)
        self.set_input_defaults("DESIGN.LP_Nmech", 4000.0, units="rpm")
        self.set_input_defaults("DESIGN.HP_Nmech", 12000.0, units="rpm")
        if ab:
            self.set_input_defaults("DESIGN.ab.Fl_I:FAR", 0.0)
        if byp:
            self.set_input_defaults("DESIGN.balance.rhs:BPR", 1.05)  # mixer extraction ratio

        self.pyc_add_pnt("OD", TwoSpool(design=False, bypass=byp, afterburner=ab))
        self.set_input_defaults("OD.fc.MN", 0.5)
        self.set_input_defaults("OD.fc.alt", 0.0, units="ft")
        self.set_input_defaults("OD.balance.rhs:FAR", 2500.0, units="degR")
        if ab:
            self.set_input_defaults("OD.ab.Fl_I:FAR", 0.0)

        # dry off-design holds the nozzle throat at its design area
        self.pyc_connect_des_od("nozz.Throat:stat:area", "wctl.a_ref")
        for el in ("lpc", "hpc"):
            for s in ("s_PR", "s_Wc", "s_eff", "s_Nc"):
                self.pyc_connect_des_od(f"{el}.{s}", f"{el}.{s}")
        for el in ("hpt", "lpt"):
            for s in ("s_PR", "s_Wp", "s_eff", "s_Np"):
                self.pyc_connect_des_od(f"{el}.{s}", f"{el}.{s}")
        areas = ["inlet", "lpc", "hpc", "burner", "hpt", "lpt"] + (["bypass_duct"] if byp else []) + (
            ["ab"] if ab else [])
        for el in areas:
            self.pyc_connect_des_od(f"{el}.Fl_O:stat:area", f"{el}.area")
        if byp:
            self.pyc_connect_des_od("splitter.Fl_O1:stat:area", "splitter.area1")
            self.pyc_connect_des_od("splitter.Fl_O2:stat:area", "splitter.area2")
            self.pyc_connect_des_od("mixer.Fl_O:stat:area", "mixer.area")
            self.pyc_connect_des_od("mixer.Fl_I1_calc:stat:area", "mixer.Fl_I1_stat_calc.area")
        super().setup()
