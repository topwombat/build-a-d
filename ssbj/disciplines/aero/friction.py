"""Flat-plate skin friction and component form factors (Raymer 1999 §12.5, pp. 281-283)."""
from __future__ import annotations

import numpy as np

FT = 0.3048


def cf_turbulent(reynolds, mach):
    """Raymer eq. 12.27: Cf = 0.455 / ((log10 R)^2.58 (1 + 0.144 M^2)^0.65)."""
    return 0.455 / (np.log10(reynolds) ** 2.58 * (1.0 + 0.144 * mach**2) ** 0.65)


def cf_laminar(reynolds):
    """Raymer eq. 12.25."""
    return 1.328 / np.sqrt(reynolds)


def cutoff_reynolds(length_m, roughness_m, mach):
    """Raymer eqs. 12.28 (subsonic) and 12.29 (transonic/supersonic); l/k is dimensionless."""
    lk = length_m / roughness_m
    if mach < 0.9:
        return 38.21 * lk**1.053
    return 44.62 * lk**1.053 * mach**1.16


def cf(length_m, mach, rho, v, mu, roughness_m, laminar_fraction=0.0):
    re = rho * v * length_m / mu
    re_t = min(re, cutoff_reynolds(length_m, roughness_m, mach))
    turb = cf_turbulent(re_t, mach)
    if laminar_fraction <= 0:
        return turb
    return laminar_fraction * cf_laminar(re) + (1 - laminar_fraction) * turb


def ff_wing(tc, x_tmax, sweep_tmax, mach):
    """Raymer eq. 12.30 (valid up to drag divergence)."""
    return (1 + 0.6 / x_tmax * tc + 100 * tc**4) * (1.34 * mach**0.18 * np.cos(sweep_tmax) ** 0.28)


def ff_fuselage(fineness):
    """Raymer eq. 12.31."""
    return 1 + 60 / fineness**3 + fineness / 400


def ff_nacelle(fineness):
    """Raymer eq. 12.32."""
    return 1 + 0.35 / fineness
