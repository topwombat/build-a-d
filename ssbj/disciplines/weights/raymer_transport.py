"""Statistical component weight build-up: Raymer (1999) cargo/transport equations.

Source: D. P. Raymer, Aircraft Design: A Conceptual Approach, 3rd ed., AIAA,
1999, §15.3, eqs. 15.25-15.44 (pp. 403-404), terminology pp. 405-407,
miscellaneous weights Table 15.3 (p. 400). The repository holds a scan of the
book. All equations are in pounds and feet; this module converts at the edges.

Raymer §15.4 (p. 407-408) warns these equations "work well for a normal
aircraft similar to the various aircraft in the database" and that a new class
(his example: Mach 3) needs class "fudge factors" derived from a similar
aircraft. No such calibration is applied here: the validation case must stay
blind (honesty rule 4). Instead every component carries an explicit 1-sigma
error and a correlated class-extrapolation factor is applied to the structure.
"""
from __future__ import annotations

import numpy as np

from ssbj.core.atmosphere import FT, LBM, atmosphere
from ssbj.core.interface import DisciplineResult, Factors, Uncertainty, Validity

LB_PER_KG = 1.0 / LBM
FT2 = FT**2
GAL_PER_KG_JETA = 1.0 / (0.80 * 3.785411784)  # Jet A at 0.80 kg/L (ASSUMPTION: nominal density)

STRUCTURE = ("wing", "vertical_tail", "fuselage", "main_gear", "nose_gear", "nacelle_group")

# Per-component 1-sigma (relative). Raymer gives no scatter statistics; these are
# judgment values fixed before the Concorde comparison was run (see decision log).
SIGMA = {
    "wing": 0.25, "vertical_tail": 0.25, "fuselage": 0.20, "main_gear": 0.15, "nose_gear": 0.15,
    "nacelle_group": 0.30, "engines": 0.30, "engine_controls": 0.30, "starter": 0.30,
    "fuel_system": 0.30, "flight_controls": 0.25, "apu": 0.20, "instruments": 0.25,
    "hydraulics": 0.30, "electrical": 0.25, "avionics": 0.20, "furnishings": 0.25,
    "passenger_furnishings": 0.25, "air_conditioning": 0.25, "anti_ice": 0.40,
    "handling_gear": 0.40, "operator_items": 0.30,
}
CLASS_SIGMA = 0.10

UNCERTAINTIES = [Uncertainty(f"weights.{k}", v, "Judgment; Raymer gives no scatter statistics.", k)
                 for k, v in SIGMA.items()] + [
    Uncertainty("weights.class_structure", CLASS_SIGMA,
                "Correlated error on all structure groups: subsonic-transport regression applied to a "
                "supersonic slender-delta transport (Raymer §15.4).", "all structure groups")]

LIMITS = [
    "Regression database is subsonic transports; slender-delta supersonic structure (thin wing, "
    "kinetic heating, high-temperature alloys) is outside it.",
    "Wing equation uses gross reference area as the 'trapezoidal' area and the planform-average "
    "quarter-chord sweep; ogee and cranked planforms are not trapezoids.",
    "Engine dry weight comes from the propulsion module scaling law (30 % sigma).",
    "No variable-geometry intake or nozzle weight beyond the nacelle-group regression.",
    "Passenger seats and lavatories from Raymer Table 15.3 averages; galleys not included.",
]


def build_weights(ac, engine_dry_weight_kg: float, payload, factors: Factors | None = None,
                  engine_length_m: float | None = None, engine_diameter_m: float | None = None) -> DisciplineResult:
    f = factors or Factors()
    d = ac.design
    wi = d.weights
    validity = Validity("weights", list(LIMITS))

    Wdg = wi.design_gross_mass_kg * LB_PER_KG
    Wl = wi.max_landing_mass_kg * LB_PER_KG
    Nz = 1.5 * wi.limit_load_factor
    w = ac.wing
    Sw = w.area / FT2
    A = w.aspect_ratio
    tc_root = float(w.tc[0])
    lam = float(w.chord[-1] / w.chord[0])
    sweep_qc = w.sweep_at(0.25)
    Scsw = wi.control_surface_area_m2 / FT2
    Bw = w.span / FT

    fus = d.fuselage
    L = fus.length_m / FT
    Df = fus.max_diameter_m / FT
    Sf = ac.fuselage.wetted_area() / FT2
    Kws = 0.75 * ((1 + 2 * lam) / (1 + lam)) * (Bw * np.tan(sweep_qc) / L)

    fin = ac.fin
    # tail arm: wing quarter-MAC to fin quarter-MAC (approximated with quarter-chord centroids)
    x_wing_qc = float(np.average(w.x_le + 0.25 * w.chord, weights=w.chord))
    x_fin_qc = fin.x_le_root + 0.5 * fin.height * np.tan(fin.sweep_le) + 0.25 * fin.mac
    Lt = max((x_fin_qc - x_wing_qc) / FT, 1.0)

    n_en = d.engine.count
    Wen = engine_dry_weight_kg * LB_PER_KG
    nac = ac.nacelles[0]
    Wec = 2.331 * Wen**0.901 * 1.0 * (1.18 if wi.thrust_reversers else 1.0)
    Sn = nac.wetted_area() / FT2  # per nacelle
    fuel_gal = wi.fuel_capacity_kg * GAL_PER_KG_JETA
    Np = wi.crew + payload.passengers
    Vpr = np.pi * (fus.max_diameter_m / 2) ** 2 * (fus.length_m - fus.nose_length_m - fus.tail_length_m) / FT**3
    Ly = 0.3 * L  # ASSUMPTION: yawing radius of gyration ~0.3 L (enters with exponent 0.07)
    Iy = Wdg * Ly**2
    # stall speed for eq. 15.29 (exponent 0.1): ASSUMPTION CLmax = 0.8 at landing weight, sea level
    rho0 = atmosphere(0.0)[2]
    v_stall_kt = np.sqrt(2 * wi.max_landing_mass_kg * 9.80665 / (rho0 * w.area * 0.8)) / 0.514444
    Lec = n_en * max((nac.x0 - 3.0) / FT, 1.0)  # engine front to cockpit (cockpit ~3 m aft of nose)
    La = 0.5 * L  # ASSUMPTION: electrical routing distance

    W = {}
    W["wing"] = (0.0051 * (Wdg * Nz) ** 0.557 * Sw**0.649 * A**0.5 * tc_root**-0.4 * (1 + lam) ** 0.1
                 * np.cos(sweep_qc) ** -1.0 * Scsw**0.1)  # 15.25
    Svt = fin.area / FT2
    W["vertical_tail"] = (0.0026 * (1 + 0.0) ** 0.225 * Wdg**0.556 * Nz**0.536 * Lt**-0.5 * Svt**0.5
                          * Lt**0.875 * np.cos(fin.sweep_quarter()) ** -1 * fin.aspect_ratio**0.35
                          * fin.tc**-0.5)  # 15.27 with Kz = Lt
    W["fuselage"] = (0.3280 * 1.0 * 1.0 * (Wdg * Nz) ** 0.5 * L**0.25 * Sf**0.302 * (1 + Kws) ** 0.04
                     * (L / Df) ** 0.10)  # 15.28, Kdoor = 1, KLg = 1
    Nl = 3.0 * 1.5  # ASSUMPTION: gear load factor 3.0
    W["main_gear"] = (0.0106 * 1.0 * Wl**0.888 * Nl**0.25 * (wi.main_gear_length_m / 0.0254) ** 0.4
                      * wi.main_wheels**0.321 * wi.main_struts**-0.5 * v_stall_kt**0.1)  # 15.29
    W["nose_gear"] = (0.032 * 1.0 * Wl**0.646 * Nl**0.2 * (wi.nose_gear_length_m / 0.0254) ** 0.5
                      * wi.nose_wheels**0.45)  # 15.30
    W["nacelle_group"] = (0.6724 * 1.0 * (nac.length / FT) ** 0.10 * (nac.width / FT) ** 0.294 * Nz**0.119
                          * Wec**0.611 * n_en**0.984 * Sn**0.224)  # 15.31
    W["engines"] = n_en * Wen
    W["engine_controls"] = 5.0 * n_en + 0.80 * Lec  # 15.32
    W["starter"] = 49.19 * (n_en * Wen / 1000) ** 0.541  # 15.33
    W["fuel_system"] = 2.405 * fuel_gal**0.606 * (1 + 1.0) ** -1.0 * (1 + 0.0) * wi.fuel_tanks**0.5  # 15.34
    Scs = Scsw  # all control surfaces are on the wing (tailless) plus rudder
    W["flight_controls"] = (145.9 * wi.control_functions**0.554 * (1 + wi.mechanical_functions /
                            wi.control_functions) ** -1.0 * Scs**0.20 * (Iy * 1e-6) ** 0.07)  # 15.35
    W["apu"] = 2.2 * wi.apu_uninstalled_kg * LB_PER_KG  # 15.36
    W["instruments"] = 4.509 * 1.0 * 1.0 * wi.crew**0.541 * n_en * (L + Bw) ** 0.5  # 15.37
    W["hydraulics"] = 0.2673 * wi.control_functions * (L + Bw) ** 0.937  # 15.38
    W["electrical"] = 7.291 * wi.electrical_kva**0.782 * La**0.346 * n_en**0.10  # 15.39
    Wuav = wi.avionics_uninstalled_kg * LB_PER_KG
    W["avionics"] = 1.73 * Wuav**0.983  # 15.40
    Wc = payload.cargo_kg * LB_PER_KG
    W["furnishings"] = 0.0577 * wi.crew**0.1 * max(Wc, 1.0) ** 0.393 * Sf**0.75  # 15.41
    # Raymer Table 15.3: passenger seat 32 lb, long-range lavatories 1.11 Npass^1.33
    W["passenger_furnishings"] = 32.0 * payload.passengers + 1.11 * payload.passengers**1.33
    W["air_conditioning"] = 62.36 * Np**0.25 * (Vpr / 1000) ** 0.604 * Wuav**0.10  # 15.42
    W["anti_ice"] = 0.002 * Wdg  # 15.43
    W["handling_gear"] = 3.0e-4 * Wdg  # 15.44

    nominal_kg = {k: v * LBM for k, v in W.items()}
    comp_kg = {}
    for k, v in nominal_kg.items():
        fac = f(f"weights.{k}")
        if k == "engines":
            fac = f("prop.weight")
        if k in STRUCTURE:
            fac *= f("weights.class_structure")
        comp_kg[k] = v * fac
    empty = sum(comp_kg.values())
    op_items = wi.operator_items_kg * f("weights.operator_items")
    crew = wi.crew * wi.crew_mass_kg
    oew = empty + op_items + crew

    for k, v in nominal_kg.items():
        if not np.isfinite(v) or v < 0:
            validity.warn(f"{k}: non-physical weight")
    if Kws > 1.0:
        validity.warn("fuselage Kws > 1: wing sweep/span outside the regression's usual range")
    if A < 2.0:
        validity.warn(f"aspect ratio {A:.2f} is far below the transport database (wing weight extrapolated)")

    return DisciplineResult(
        "weights",
        "Raymer (1999) cargo/transport statistical group weights, eqs. 15.25-15.44",
        {"components_kg": comp_kg, "components_nominal_kg": nominal_kg, "empty_kg": empty,
         "operator_items_kg": op_items, "crew_kg": crew, "oew_kg": oew,
         "inputs": {"Nz": Nz, "Sw_ft2": Sw, "A": A, "tc_root": tc_root, "taper": lam,
                    "sweep_qc_deg": float(np.degrees(sweep_qc)), "Lt_ft": Lt, "Kws": Kws,
                    "fuel_gal": fuel_gal, "v_stall_kt": v_stall_kt}},
        UNCERTAINTIES,
        validity,
    )
