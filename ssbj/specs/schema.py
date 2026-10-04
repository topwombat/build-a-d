"""Typed, validated case file: mission requirements plus the design parameter vector.

A case file (YAML) has three top-level blocks:

``mission``   what the aircraft must do (payload, range, Mach, altitudes,
              reserves, field length and the full flight profile).
``design``    the parameter vector the disciplines analyse (geometry, engine
              cycle variables, design weights). In Phase 3 the optimizer owns it.
``provenance`` for every numeric leaf in ``mission`` and ``design``, where the
              value came from: a citation, or ``ASSUMPTION: <reason>``. Validation
              cases are rejected if any leaf lacks an entry (honesty rule 3).

The JSON schema is exported to ``ssbj/specs/case.schema.json`` by
``python -m ssbj schema``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------- mission
class Payload(_M):
    passengers: int = Field(ge=0)
    mass_per_passenger_kg: float = Field(gt=0, description="passenger plus baggage")
    cargo_kg: float = Field(0.0, ge=0)

    @property
    def mass_kg(self) -> float:
        return self.passengers * self.mass_per_passenger_kg + self.cargo_kg


class Taxi(_M):
    segment: Literal["taxi"]
    name: str = "taxi"
    minutes: float = Field(ge=0)
    thrust_fraction_of_sls_dry: float = Field(0.05, gt=0, le=1)


class Takeoff(_M):
    segment: Literal["takeoff"]
    name: str = "takeoff"
    minutes: float = Field(gt=0)
    power: Literal["max_dry", "max_reheat"] = "max_reheat"


class Climb(_M):
    """Climb and/or accelerate along a straight line in (Mach, altitude) to the end point.

    Integrated in energy height: each step uses specific excess power at the
    selected power setting. ``power: max_reheat`` is the transonic acceleration.
    """

    segment: Literal["climb"]
    name: str
    to_mach: float = Field(gt=0, le=3)
    to_altitude_ft: float = Field(ge=0, le=70000)
    power: Literal["max_dry", "max_reheat"]


class FixedCruise(_M):
    """Cruise a fixed distance at fixed Mach and altitude (e.g. a subsonic overland leg)."""

    segment: Literal["cruise_fixed"]
    name: str
    distance_nmi: float = Field(ge=0)
    mach: float = Field(gt=0, le=3)
    altitude_ft: float = Field(ge=0, le=70000)


class RangeCruise(_M):
    """The range-filling cruise: constant Mach, cruise-climb within the altitude band."""

    segment: Literal["cruise"]
    name: str = "cruise"


class Descent(_M):
    segment: Literal["descent"]
    name: str = "descent"
    to_altitude_ft: float = Field(0.0, ge=0)
    to_mach: float = Field(0.3, gt=0)
    lift_to_drag_glide: float | None = Field(
        None, gt=0, description="if omitted, the aero polar at idle is used")


Segment = Annotated[Union[Taxi, Takeoff, Climb, FixedCruise, RangeCruise, Descent], Field(discriminator="segment")]


class CruiseSpec(_M):
    mach: float = Field(gt=0, le=3)
    altitude_min_ft: float = Field(ge=0, le=70000)
    altitude_max_ft: float = Field(ge=0, le=70000)
    mode: Literal["cruise_climb", "constant_altitude"] = "cruise_climb"

    @model_validator(mode="after")
    def _band(self):
        if self.altitude_max_ft < self.altitude_min_ft:
            raise ValueError("cruise altitude_max_ft < altitude_min_ft")
        return self


class Reserves(_M):
    contingency_fraction_of_trip: float = Field(ge=0, le=0.5)
    diversion_nmi: float = Field(ge=0)
    diversion_mach: float = Field(gt=0, le=1.0)
    diversion_altitude_ft: float = Field(ge=0, le=45000)
    hold_minutes: float = Field(ge=0)
    hold_altitude_ft: float = Field(ge=0, le=45000)
    hold_mach: float = Field(gt=0, le=1.0)


class Mission(_M):
    payload: Payload
    design_range_nmi: float = Field(gt=0, description="trip distance for the fuel-burn evaluation")
    cruise: CruiseSpec
    reserves: Reserves
    field_length_ft: float | None = Field(None, gt=0, description="reported in Phase 4; not evaluated yet")
    takeoff_noise: str | None = None
    sonic_boom: Literal["report", "constrain"] = "report"
    profile: list[Segment]

    @field_validator("profile")
    @classmethod
    def _profile(cls, v):
        kinds = [s.segment for s in v]
        if kinds.count("cruise") != 1:
            raise ValueError("profile must contain exactly one range-filling 'cruise' segment")
        if "takeoff" not in kinds:
            raise ValueError("profile must contain a 'takeoff' segment")
        if kinds.index("takeoff") > kinds.index("cruise"):
            raise ValueError("takeoff must come before cruise")
        return v


# --------------------------------------------------------------------------- design
class WingStation(_M):
    y_m: float = Field(ge=0)
    x_le_m: float
    chord_m: float = Field(ge=0)
    tc: float = Field(gt=0, lt=0.3)


class Wing(_M):
    stations: list[WingStation] = Field(min_length=2)
    max_thickness_chord_fraction: float = Field(0.5, gt=0.1, lt=0.9)


class Fuselage(_M):
    length_m: float = Field(gt=0)
    max_diameter_m: float = Field(gt=0)
    nose_length_m: float = Field(gt=0)
    tail_length_m: float = Field(gt=0)
    tail_end_diameter_m: float = Field(0.0, ge=0)
    cabin_pressure_differential_psi: float = Field(gt=0)


class FinSpec(_M):
    x_le_root_m: float
    root_chord_m: float = Field(gt=0)
    tip_chord_m: float = Field(ge=0)
    height_m: float = Field(gt=0)
    sweep_le_deg: float = Field(ge=0, lt=85)
    tc: float = Field(gt=0, lt=0.3)


class NacelleSpec(_M):
    y_m: list[float] = Field(min_length=1, description="starboard nacelle centreline positions")
    x_inlet_m: float
    z_m: float
    length_m: float = Field(gt=0)
    width_m: float = Field(gt=0)
    height_m: float = Field(gt=0)
    capture_area_m2: float = Field(gt=0)


class Engine(_M):
    type: Literal["ab_turbojet"] = "ab_turbojet"
    count: int = Field(ge=1, le=8)
    fn_sls_dry_kN: float = Field(gt=0, description="dry SLS thrust per engine at the design point")
    opr: float = Field(gt=2, lt=60)
    t4_max_K: float = Field(gt=1000, lt=2200)
    t_ab_K: float = Field(gt=1200, lt=2400, description="afterburner exit temperature at full reheat")
    comp_eff: float = Field(0.85, gt=0.6, lt=0.95)
    turb_eff: float = Field(0.88, gt=0.6, lt=0.96)
    nozzle_cv: float = Field(0.99, gt=0.9, le=1.0)
    customer_bleed_fraction: float = Field(0.0, ge=0, lt=0.1)


class WeightsInputs(_M):
    design_gross_mass_kg: float = Field(gt=0, description="MTOW used by the statistical equations")
    max_landing_mass_kg: float = Field(gt=0)
    fuel_capacity_kg: float = Field(gt=0)
    limit_load_factor: float = Field(gt=1)
    crew: int = Field(ge=1)
    crew_mass_kg: float = Field(gt=0)
    main_gear_length_m: float = Field(gt=0)
    nose_gear_length_m: float = Field(gt=0)
    main_wheels: int = Field(ge=1)
    main_struts: int = Field(ge=1)
    nose_wheels: int = Field(ge=1)
    fuel_tanks: int = Field(ge=1)
    hydraulic_functions: int = Field(ge=1)
    control_functions: int = Field(ge=1)
    mechanical_functions: int = Field(ge=0)
    electrical_kva: float = Field(gt=0)
    avionics_uninstalled_kg: float = Field(gt=0)
    apu_uninstalled_kg: float = Field(ge=0)
    control_surface_area_m2: float = Field(gt=0)
    operator_items_kg: float = Field(ge=0, description="operational items added to empty weight")
    thrust_reversers: bool = False


class Design(_M):
    wing: Wing
    fuselage: Fuselage
    fin: FinSpec
    nacelles: NacelleSpec
    engine: Engine
    weights: WeightsInputs


# --------------------------------------------------------------------------- case
class Case(_M):
    schema_version: Literal[1] = 1
    name: str
    description: str = ""
    validation_case: bool = False
    mission: Mission
    design: Design
    provenance: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _provenance_complete(self):
        if self.validation_case:
            missing = [p for p in numeric_leaves(self.model_dump(include={"mission", "design"}))
                       if not _covered(p, self.provenance)]
            if missing:
                raise ValueError("validation case without provenance for: " + ", ".join(missing))
        return self


def numeric_leaves(obj, prefix: str = "") -> list[str]:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += numeric_leaves(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += numeric_leaves(v, f"{prefix}[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out.append(prefix)
    return out


def _covered(path: str, prov: dict[str, str]) -> bool:
    """A leaf is covered by its own key or any ancestor key (e.g. 'design.wing.stations')."""
    p = path
    while True:
        if p in prov:
            return True
        cut = max(p.rfind("."), p.rfind("["))
        if cut <= 0:
            return False
        p = p[:cut]


def load_case(path: str | Path) -> Case:
    data = yaml.safe_load(Path(path).read_text())
    return Case.model_validate(data)


def json_schema() -> dict:
    return Case.model_json_schema()
