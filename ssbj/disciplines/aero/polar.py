"""Low-rung drag polar: CD = CD0_friction(M, h) + CD_misc + CD_wave(M) + K(M) CL^2.

Assembled from friction.py (component build-up), wave_drag.py (Harris area
rule) and lift.py (linear theory). Tables are built once per geometry and
interpolated by the mission analysis.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import RegularGridInterpolator

from ssbj.core.atmosphere import FT, atmosphere
from ssbj.core.interface import DisciplineResult, Factors, Uncertainty, Validity
from ssbj.disciplines.aero import friction as fr
from ssbj.disciplines.aero.lift import cl_alpha, k_factor
from ssbj.disciplines.aero.wave_drag import harris_wave_drag, raymer_wave_drag

MACH_GRID = np.array([0.2, 0.4, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.3, 1.4, 1.5,
                      1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.4])
ALT_GRID_FT = np.arange(0.0, 70001.0, 5000.0)

# Smooth paint, Raymer (1999) Table 12.4, k = 2.08e-5 ft
ROUGHNESS_M = 2.08e-5 * FT
# Leakage and protuberance drag as a fraction of friction drag. ASSUMPTION: Raymer §12.5
# gives percentage allowances by aircraft class; 5 % is used with a 50 % 1-sigma.
LP_FRACTION = 0.05
# Leading-edge suction fraction for a thin, highly swept SST wing. ASSUMPTION (no
# calibration): mostly-separated leading-edge flow, S = 0.2 with a 15 % sigma on K.
SUCTION = 0.2
M_WAVE_START = 0.90  # wave/drag-rise onset used for the transonic fairing
M_HARRIS_MIN = 1.1

UNCERTAINTIES = [
    Uncertainty("aero.friction", 0.08,
                "Judgment: turbulent flat-plate correlation, form factors and wetted areas; "
                "no supersonic-transport validation data in Phase 1.", "CD0 friction + misc"),
    Uncertainty("aero.misc", 0.50, "Leakage/protuberance allowance is a class-average assumption.",
                "CD misc"),
    Uncertainty("aero.wave", 0.25,
                "Judgment: far-field linear area rule with a thin-wing and smoothed-nacelle model; "
                "the Raymer eq. 12.46 cross-check is reported alongside.", "CD wave, M >= 1.2"),
    Uncertainty("aero.wave_transonic", 0.40,
                "Fairing between drag-rise onset and the first Harris point has no physics; "
                "widened deliberately.", "CD wave, 0.9 < M < 1.2"),
    Uncertainty("aero.K", 0.15,
                "Leading-edge suction fraction is assumed, not computed; linear theory ignores "
                "vortex lift.", "drag due to lift"),
]

LIMITS = [
    "Linear theory: invalid at high angle of attack where leading-edge vortex lift dominates "
    "(take-off, approach); no vortex lift is modelled.",
    "Transonic (0.9 < M < 1.2) wave drag is a fairing, not a prediction.",
    "Harris area rule assumes slender, smooth configurations; blunt bases, inlet spillage and "
    "boundary-layer diverters are not modelled.",
    "No trim drag (stability module is Phase 4).",
    "No interference factors (Q = 1).",
]


@dataclass
class AeroPolar:
    mach: np.ndarray
    alt_ft: np.ndarray
    cd0_friction: np.ndarray  # (n_mach, n_alt), includes form factors
    cd_misc_frac: float
    cd_wave: np.ndarray  # (n_mach,)
    k: np.ndarray  # (n_mach,)
    cla: np.ndarray  # (n_mach,)
    s_ref: float

    def __post_init__(self):
        self._f = RegularGridInterpolator((self.mach, self.alt_ft), self.cd0_friction,
                                          bounds_error=False, fill_value=None)

    def cd(self, mach, alt_ft, cl, factors: Factors | None = None):
        f = factors or Factors()
        mach = np.asarray(mach, dtype=float)
        alt_ft = np.asarray(alt_ft, dtype=float)
        cf = self._f(np.stack([mach, alt_ft], axis=-1)) * f("aero.friction")
        misc = cf * self.cd_misc_frac * f("aero.misc")
        wave = np.interp(mach, self.mach, self.cd_wave)
        wf = np.where(mach >= 1.2, f("aero.wave"), f("aero.wave_transonic"))
        k = np.interp(mach, self.mach, self.k) * f("aero.K")
        return cf + misc + wave * wf + k * np.asarray(cl) ** 2

    def breakdown(self, mach, alt_ft, cl):
        cf = float(self._f([[mach, alt_ft]])[0])
        return {
            "cd0_friction": cf,
            "cd_misc": cf * self.cd_misc_frac,
            "cd_wave": float(np.interp(mach, self.mach, self.cd_wave)),
            "cd_lift": float(np.interp(mach, self.mach, self.k)) * cl**2,
        }

    def to_dict(self):
        return {
            "mach": self.mach.tolist(), "alt_ft": self.alt_ft.tolist(),
            "cd0_friction": self.cd0_friction.tolist(), "cd_misc_frac": self.cd_misc_frac,
            "cd_wave": self.cd_wave.tolist(), "k": self.k.tolist(), "cla": self.cla.tolist(),
            "s_ref": self.s_ref,
        }


def _friction_table(ac) -> np.ndarray:
    swet = ac.wetted_areas()
    lengths = ac.component_lengths()
    d = ac.design
    tmax = d.wing.max_thickness_chord_fraction
    sweep_tmax = ac.wing.sweep_at(tmax)
    tc_w = float(np.average(ac.wing.tc, weights=ac.wing.chord))
    f_fus = d.fuselage.length_m / d.fuselage.max_diameter_m
    f_nac = ac.nacelles[0].fineness if ac.nacelles else 10.0
    sweep_fin = ac.fin.sweep_quarter()
    out = np.zeros((len(MACH_GRID), len(ALT_GRID_FT)))
    for i, m in enumerate(MACH_GRID):
        for j, h in enumerate(ALT_GRID_FT):
            T, p, rho, a, mu = atmosphere(h * FT)
            v = m * a
            total = 0.0
            for comp in ("wing", "fuselage", "fin", "nacelles"):
                c = fr.cf(lengths[comp], m, rho, v, mu, ROUGHNESS_M)
                if m >= 1.0:  # Raymer eq. 12.42: no form factors supersonically
                    ff = 1.0
                elif comp == "wing":
                    ff = fr.ff_wing(tc_w, tmax, sweep_tmax, m)
                elif comp == "fin":
                    ff = fr.ff_wing(ac.fin.tc, 0.5, sweep_fin, m)
                elif comp == "fuselage":
                    ff = fr.ff_fuselage(f_fus)
                else:
                    ff = fr.ff_nacelle(f_nac)
                total += c * ff * swet[comp]
            out[i, j] = total / ac.s_ref
    return out


def build_polar(ac) -> DisciplineResult:
    validity = Validity("aerodynamics", list(LIMITS))
    cd0f = _friction_table(ac)

    sup = MACH_GRID[MACH_GRID >= M_HARRIS_MIN]
    wave_sup = np.array([harris_wave_drag(ac, m)["D_q"] / ac.s_ref for m in sup])
    # transonic fairing: cubic Hermite from (M_WAVE_START, 0, slope 0) to the first Harris point
    m1, w1 = sup[0], wave_sup[0]
    slope1 = (wave_sup[1] - wave_sup[0]) / (sup[1] - sup[0])
    wave = np.zeros_like(MACH_GRID)
    for i, m in enumerate(MACH_GRID):
        if m >= M_HARRIS_MIN:
            wave[i] = wave_sup[np.searchsorted(sup, m)]
        elif m > M_WAVE_START:
            t = (m - M_WAVE_START) / (m1 - M_WAVE_START)
            h = m1 - M_WAVE_START
            wave[i] = w1 * (3 * t**2 - 2 * t**3) + slope1 * h * (t**3 - t**2)
    wave = np.maximum(wave, 0.0)

    w = ac.wing
    r_fus = ac.fuselage_radius_at_wing
    s_exp_ratio = w.exposed_area(r_fus) / w.area
    sweep_tmax = w.sweep_at(ac.design.wing.max_thickness_chord_fraction)
    sweep_le = w.le_sweep_area_weighted()
    cla = np.array([cl_alpha(w.aspect_ratio, m, sweep_tmax, s_exp_ratio,
                             ac.design.fuselage.max_diameter_m, w.span) for m in MACH_GRID])
    k = np.array([k_factor(w.aspect_ratio, m, c, sweep_le, SUCTION) for m, c in zip(MACH_GRID, cla)])

    polar = AeroPolar(MACH_GRID, ALT_GRID_FT, cd0f, LP_FRACTION, wave, k, cla, ac.s_ref)

    # independent cross-check of the wave drag (reported, not used)
    check = {f"M{m:.1f}": {"harris": float(np.interp(m, MACH_GRID, wave)),
                           "raymer_12_46_EWD_1.4": raymer_wave_drag(ac, m, 1.4) / ac.s_ref,
                           "raymer_12_46_EWD_2.0": raymer_wave_drag(ac, m, 2.0) / ac.s_ref}
             for m in (1.3, 1.6, 2.0)}
    for v in check.values():
        if not (0.5 * v["raymer_12_46_EWD_1.4"] <= v["harris"] <= 1.5 * v["raymer_12_46_EWD_2.0"]):
            validity.warn("Harris wave drag falls outside the Raymer E_WD 1.4-2.0 band by more than 50 %")
    if w.aspect_ratio > 3.0:
        validity.warn("aspect ratio > 3: the delta-wing supersonic lift model is a poor fit")

    return DisciplineResult(
        "aerodynamics",
        "component skin friction (Raymer 12.25-12.33) + Harris area-rule wave drag + "
        "linear-theory lift with leading-edge-suction K (Raymer 12.6)",
        {"polar": polar, "wave_crosscheck": check, "wetted_areas_m2": ac.wetted_areas(),
         "s_ref_m2": ac.s_ref, "aspect_ratio": w.aspect_ratio, "sweep_le_deg": float(np.degrees(sweep_le))},
        UNCERTAINTIES,
        validity,
    )
