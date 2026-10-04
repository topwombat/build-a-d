"""OpenMDAO assembly: geometry -> aerodynamics, propulsion -> weights -> mission.

Continuous inputs are the parts of the parameter vector an optimizer will own
in Phase 3 (the four engine cycle variables, a wing-size scale, the design
weights). Objects that are not vectors (geometry, polar, engine deck) pass
between components as OpenMDAO discrete variables. Expensive components
memoise on their inputs so repeated runs (Monte Carlo, optimizer line
searches) only redo what changed. Derivatives are not provided in Phase 1.
"""
from __future__ import annotations

import copy
import json

import numpy as np
import openmdao.api as om

from ssbj.core.interface import Factors
from ssbj.disciplines.aero.polar import build_polar
from ssbj.disciplines.mission.analysis import analyse
from ssbj.disciplines.propulsion.deck import build_engine
from ssbj.disciplines.weights.raymer_transport import build_weights
from ssbj.geometry.parametric import build as build_geometry


def _key(*vals) -> str:
    return json.dumps([np.asarray(v).tolist() if not isinstance(v, (str, dict)) else v for v in vals],
                      sort_keys=True, default=str)


class _Memo(om.ExplicitComponent):
    def initialize(self):
        self.options.declare("case", recordable=False)
        self.options.declare("results", default=None, recordable=False,
                             desc="dict collecting DisciplineResult objects for reporting")
        self._memo = {}

    def _store(self, name, result):
        if self.options["results"] is not None:
            self.options["results"][name] = result


class GeometryComp(_Memo):
    def setup(self):
        self.add_input("wing_chord_scale", 1.0, desc="uniform scale on wing chords (planform size)")
        self.add_discrete_output("aircraft", None)
        self.add_output("s_ref", 0.0, units="m**2")
        self.add_output("wing_fuel_volume", 0.0, units="m**3")

    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        k = _key(inputs["wing_chord_scale"])
        if k not in self._memo:
            d = copy.deepcopy(self.options["case"].design)
            for s in d.wing.stations:
                s.chord_m *= float(inputs["wing_chord_scale"][0])
            self._memo = {k: build_geometry(d)}
        ac = self._memo[k]
        discrete_outputs["aircraft"] = ac
        outputs["s_ref"] = ac.s_ref
        outputs["wing_fuel_volume"] = ac.wing_fuel_volume()


class AeroComp(_Memo):
    def setup(self):
        self.add_discrete_input("aircraft", None)
        self.add_discrete_output("polar", None)
        self.add_output("cd0_cruise", 0.0)
        self.add_output("ld_max_cruise", 0.0)

    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        ac = discrete_inputs["aircraft"]
        k = id(ac)
        if k not in self._memo:
            self._memo = {k: build_polar(ac)}
        res = self._memo[k]
        self._store("aerodynamics", res)
        polar = res.outputs["polar"]
        discrete_outputs["polar"] = polar
        c = self.options["case"].mission.cruise
        h = 0.5 * (c.altitude_min_ft + c.altitude_max_ft)
        outputs["cd0_cruise"] = float(polar.cd(c.mach, h, 0.0))
        k_ = float(np.interp(c.mach, polar.mach, polar.k))
        outputs["ld_max_cruise"] = 1.0 / (2.0 * np.sqrt(k_ * float(outputs["cd0_cruise"][0])))


class PropulsionComp(_Memo):
    def setup(self):
        self.add_input("opr", 15.0)
        self.add_input("t4_max", 1500.0, units="K")
        self.add_input("fn_sls_dry", 100.0, units="kN")
        self.add_input("t_ab", 1800.0, units="K")
        self.add_discrete_output("deck", None)
        self.add_output("engine_dry_mass", 0.0, units="kg")
        self.add_output("fn_sls_reheat", 0.0, units="kN")
        self.add_output("tsfc_cruise", 0.0, units="1/h")

    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        e = self.options["case"].design.engine.model_copy(update={
            "opr": float(inputs["opr"][0]), "t4_max_K": float(inputs["t4_max"][0]),
            "fn_sls_dry_kN": float(inputs["fn_sls_dry"][0]), "t_ab_K": float(inputs["t_ab"][0])})
        k = _key(e.model_dump())
        if k not in self._memo:
            self._memo = {k: build_engine(e)}
        res = self._memo[k]
        self._store("propulsion", res)
        deck = res.outputs["deck"]
        discrete_outputs["deck"] = deck
        outputs["engine_dry_mass"] = res.outputs["engine_dry_weight_kg"]
        outputs["fn_sls_reheat"] = res.outputs["fn_sls_reheat_kN"]
        c = self.options["case"].mission.cruise
        h = 0.5 * (c.altitude_min_ft + c.altitude_max_ft)
        t = deck.max_thrust(c.mach, h, reheat=False) * 0.8
        ff, _ = deck.fuel_flow_at_thrust(c.mach, h, t)
        outputs["tsfc_cruise"] = ff * 9.80665 / t * 3600.0


class WeightsComp(_Memo):
    def initialize(self):
        super().initialize()
        self.options.declare("factors", default=None, recordable=False)

    def setup(self):
        self.add_discrete_input("aircraft", None)
        self.add_input("engine_dry_mass", 0.0, units="kg")
        self.add_output("oew", 0.0, units="kg")

    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        case = self.options["case"]
        res = build_weights(discrete_inputs["aircraft"], float(inputs["engine_dry_mass"][0]),
                            case.mission.payload, self.options["factors"])
        self._store("weights", res)
        outputs["oew"] = res.outputs["oew_kg"]


class MissionComp(_Memo):
    def initialize(self):
        super().initialize()
        self.options.declare("factors", default=None, recordable=False)

    def setup(self):
        self.add_discrete_input("polar", None)
        self.add_discrete_input("deck", None)
        self.add_input("s_ref", 0.0, units="m**2")
        self.add_input("oew", 0.0, units="kg")
        self.add_input("mtow", 0.0, units="kg")
        self.add_input("fuel_capacity", 0.0, units="kg")
        self.add_output("range", 0.0, units="nmi")
        self.add_output("range_trip_fuel", 0.0, units="kg")
        self.add_output("design_ramp_fuel", 0.0, units="kg")
        self.add_output("design_trip_fuel", 0.0, units="kg")
        self.add_output("design_block_fuel", 0.0, units="kg")
        self.add_output("transonic_thrust_margin", 0.0)

    def compute(self, inputs, outputs, discrete_inputs, discrete_outputs):
        case = self.options["case"]
        res = analyse(case.mission, discrete_inputs["polar"], discrete_inputs["deck"],
                      float(inputs["s_ref"][0]), float(inputs["oew"][0]), float(inputs["mtow"][0]),
                      float(inputs["fuel_capacity"][0]), self.options["factors"])
        self._store("mission", res)
        r, dm = res.outputs["range"], res.outputs["design_mission"]
        outputs["range"] = r["range_nmi"]
        outputs["range_trip_fuel"] = r["trip_fuel_kg"]
        outputs["design_ramp_fuel"] = dm["ramp_fuel_kg"]
        outputs["design_trip_fuel"] = dm["trip_fuel_kg"]
        outputs["design_block_fuel"] = dm["block_fuel_kg"]
        outputs["transonic_thrust_margin"] = min(r["transonic_thrust_margin"], dm["transonic_thrust_margin"])


class SSBJModel(om.Group):
    def initialize(self):
        self.options.declare("case", recordable=False)
        self.options.declare("results", default=None, recordable=False)
        self.options.declare("factors", default=None, recordable=False)

    def setup(self):
        c, r, f = self.options["case"], self.options["results"], self.options["factors"]
        ivc = self.add_subsystem("dv", om.IndepVarComp(), promotes=["*"])
        e, w = c.design.engine, c.design.weights
        ivc.add_output("wing_chord_scale", 1.0)
        ivc.add_output("opr", e.opr)
        ivc.add_output("t4_max", e.t4_max_K, units="K")
        ivc.add_output("fn_sls_dry", e.fn_sls_dry_kN, units="kN")
        ivc.add_output("t_ab", e.t_ab_K, units="K")
        ivc.add_output("mtow", w.design_gross_mass_kg, units="kg")
        ivc.add_output("fuel_capacity", w.fuel_capacity_kg, units="kg")
        self.add_subsystem("geometry", GeometryComp(case=c, results=r), promotes=["*"])
        self.add_subsystem("aero", AeroComp(case=c, results=r), promotes=["*"])
        self.add_subsystem("propulsion", PropulsionComp(case=c, results=r), promotes=["*"])
        self.add_subsystem("weights", WeightsComp(case=c, results=r, factors=f), promotes=["*"])
        self.add_subsystem("mission", MissionComp(case=c, results=r, factors=f), promotes=["*"])


def make_problem(case, factors: Factors | None = None, results: dict | None = None) -> om.Problem:
    p = om.Problem(SSBJModel(case=case, results=results, factors=factors), reports=False)
    p.setup()
    return p
