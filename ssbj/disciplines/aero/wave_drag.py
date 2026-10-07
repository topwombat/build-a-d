"""Supersonic area-rule wave drag (far-field, linear theory).

Method (Harris, NASA TM X-947, 1964; summarised in Raymer 1999 §12.5, pp. 290-292):
for each roll angle theta the aircraft is cut by Mach planes, the intercepted
areas projected onto the plane normal to the freestream give an equivalent
body area distribution S(x; theta), and the von Karman slender-body integral
gives its drag. The aircraft wave drag is the average over theta.

The slender-body integral is evaluated with the Fourier-sine method: with
x = (l/2)(1 - cos phi) and S'(x) = l * sum_n A_n sin(n phi),

    D/q = (pi l^2 / 4) * sum_n n A_n^2

S(x) itself is fitted by linear least squares to the integrated basis
functions, which avoids differentiating sampled areas. The constant is
verified against the Sears-Haack closed form (Raymer eq. 12.45) in
tests/test_wave_drag.py.
"""
from __future__ import annotations

import numpy as np


def _basis(phi: np.ndarray, n_terms: int) -> np.ndarray:
    """G_n(phi) = integral_0^phi sin(n p) sin(p) dp, so that S = (l^2/2) sum A_n G_n."""
    cols = []
    for n in range(1, n_terms + 1):
        if n == 1:
            g = phi / 2.0 - np.sin(2 * phi) / 4.0
        else:
            g = np.sin((n - 1) * phi) / (2 * (n - 1)) - np.sin((n + 1) * phi) / (2 * (n + 1))
        cols.append(g)
    return np.stack(cols, axis=1)


def slender_body_drag(x: np.ndarray, area: np.ndarray, n_terms: int = 40) -> float:
    """von Karman wave drag D/q (m^2) of an area distribution sampled on x.

    The distribution is taken between its first and last non-zero samples. A
    non-zero end area is allowed in the fit but its base drag is not modelled.
    """
    x = np.asarray(x, dtype=float)
    a = np.asarray(area, dtype=float)
    nz = np.nonzero(a > 1e-12 * max(a.max(), 1e-30))[0]
    if len(nz) < 3:
        return 0.0
    i0, i1 = max(nz[0] - 1, 0), min(nz[-1] + 1, len(x) - 1)
    xs, s = x[i0 : i1 + 1], a[i0 : i1 + 1]
    l = xs[-1] - xs[0]
    phi = np.arccos(np.clip(1.0 - 2.0 * (xs - xs[0]) / l, -1, 1))
    n_terms = min(n_terms, max(len(xs) // 3, 3))
    G = _basis(phi, n_terms) * (l**2 / 2.0)
    A, *_ = np.linalg.lstsq(G, s, rcond=None)
    n = np.arange(1, n_terms + 1)
    return float(np.pi * l**2 / 4.0 * np.sum(n * A**2))


def sears_haack_area(x: np.ndarray, length: float, a_max: float) -> np.ndarray:
    """Sears-Haack body area, Raymer (1999) eq. 12.43 with x measured from the nose."""
    xi = (np.asarray(x) - length / 2.0) / (length / 2.0)
    return a_max * np.clip(1.0 - xi**2, 0.0, None) ** 1.5


def sears_haack_drag(length: float, a_max: float) -> float:
    """Raymer (1999) eq. 12.45: D/q = (9 pi / 2) (A_max / l)^2."""
    return 4.5 * np.pi * (a_max / length) ** 2


def harris_wave_drag(aircraft, mach: float, n_theta: int = 36, n_x: int = 721,
                     x_end: float | None = None) -> dict:
    """Wave drag D/q (m^2) of the full configuration at ``mach`` (> 1).

    ``x_end`` is for wind-tunnel models on a sting: the cuts stop at x_end + reach,
    where every cut still crosses the constant-area sting (the body must extend
    past x_end + 2 reach). The area there is the base area with S' = 0, which the
    sine series represents exactly; closing the sting with a step instead adds a
    spurious base-closure drag.

    Returns the average over roll angles plus the per-angle values for inspection.
    Roll angles are taken on [0, pi) and the result uses the left/right symmetry
    of the configuration (theta and theta + pi give mirror-image cuts only for
    planar configurations; the fin breaks this, so the full circle is sampled).
    """
    if mach <= 1.0:
        raise ValueError("Harris wave drag is defined for M > 1")
    B = np.sqrt(mach**2 - 1.0)
    span = aircraft.wing.span
    height = (aircraft.fin.z_root + aircraft.fin.height) if aircraft.fin is not None else \
        float(np.max(aircraft.fuselage.radius(np.linspace(0, aircraft.fuselage.length, 200))))
    L = aircraft.length
    thetas = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    out = []
    for th in thetas:
        reach = B * (abs(np.cos(th)) * span / 2 + abs(np.sin(th)) * height) + 2.0
        x0 = np.linspace(-reach, (L if x_end is None else x_end) + reach, n_x)
        s = aircraft.mach_plane_areas(mach, th, x0)
        out.append(slender_body_drag(x0, s))
    out = np.array(out)
    return {"D_q": float(out.mean()), "per_theta": out.tolist(), "thetas": thetas.tolist()}


def raymer_wave_drag(aircraft, mach: float, e_wd: float) -> float:
    """Raymer (1999) eq. 12.46 empirical correlation; used as an independent cross-check.

    A_max excludes the inlet capture area (as Raymer instructs); the length is
    the overall length. Valid for M >= 1.2.
    """
    x = np.linspace(0, aircraft.length, 400)
    a = aircraft.mach_plane_areas(1.0, 0.0, x)
    a_max = float(a.max())  # nacelle shells only: capture area already removed
    lam = np.degrees(aircraft.wing.le_sweep_area_weighted())
    corr = 1.0 - 0.386 * (mach - 1.2) ** 0.57 * (1.0 - np.pi * lam**0.77 / 100.0)
    return e_wd * corr * sears_haack_drag(aircraft.length, a_max)
