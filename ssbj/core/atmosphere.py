"""U.S. Standard Atmosphere 1976, geopotential layers up to 32 km.

Layer constants are the defining values of the standard (NOAA/NASA/USAF,
U.S. Standard Atmosphere 1976, NOAA-S/T 76-1562, Table 4). The implementation is
cross-checked against pyCycle's independent ambient model in
tests/test_atmosphere.py.
"""
from __future__ import annotations

import numpy as np

G0 = 9.80665  # m/s^2
R_AIR = 287.05287  # J/(kg K)
GAMMA = 1.4

# base geopotential altitude (m), base temperature (K), lapse rate (K/m)
_LAYERS = [
    (0.0, 288.15, -0.0065),
    (11000.0, 216.65, 0.0),
    (20000.0, 216.65, 0.001),
    (32000.0, 228.65, 0.0028),
]
_P0 = 101325.0


def _base_pressures():
    p = [_P0]
    for (h0, t0, a), (h1, _, _) in zip(_LAYERS[:-1], _LAYERS[1:]):
        p.append(_layer_p(h1, h0, t0, a, p[-1]))
    return p


def _layer_p(h, h0, t0, a, p0):
    if a == 0.0:
        return p0 * np.exp(-G0 * (h - h0) / (R_AIR * t0))
    t = t0 + a * (h - h0)
    return p0 * (t / t0) ** (-G0 / (a * R_AIR))


_PB = _base_pressures()


def atmosphere(alt_m):
    """Return (T [K], p [Pa], rho [kg/m^3], a [m/s], mu [Pa s]) at a pressure altitude.

    Altitudes throughout the pipeline are pressure (geopotential) altitudes, the
    convention of flight levels and of pyCycle's ambient model.
    """
    h = np.atleast_1d(np.asarray(alt_m, dtype=float))
    if np.any(h < -1000) or np.any(h > 32000):
        raise ValueError("altitude outside the implemented 1976 standard range (-1 km to 32 km)")
    T = np.empty_like(h)
    p = np.empty_like(h)
    for i, (h0, t0, a) in enumerate(_LAYERS):
        hi = _LAYERS[i + 1][0] if i + 1 < len(_LAYERS) else np.inf
        m = (h >= h0) & (h < hi) if i > 0 else (h < hi)
        T[m] = t0 + a * (h[m] - h0)
        p[m] = _layer_p(h[m], h0, t0, a, _PB[i])
    rho = p / (R_AIR * T)
    a_snd = np.sqrt(GAMMA * R_AIR * T)
    mu = 1.458e-6 * T**1.5 / (T + 110.4)  # Sutherland, as in the 1976 standard
    if np.ndim(alt_m) == 0:
        return float(T[0]), float(p[0]), float(rho[0]), float(a_snd[0]), float(mu[0])
    return T, p, rho, a_snd, mu


FT = 0.3048
NMI = 1852.0
LBF = 4.4482216152605
LBM = 0.45359237
