"""Linear-theory lift-curve slope and drag-due-to-lift factor across the Mach range.

Subsonic CL_alpha: DATCOM/Helmbold form, Raymer (1999) eq. 12.6.
Supersonic CL_alpha: linear theory for a delta wing of the same aspect ratio
(semi-apex angle tan(eps) = AR/4). Subsonic leading edge (beta tan(eps) < 1):
CL_alpha = 2 pi tan(eps) / E(k), k = sqrt(1 - beta^2 tan^2 eps) (Stewart 1946;
Brown, NACA TN 1183, 1946). Supersonic leading edge: CL_alpha = 4 / beta.

Drag due to lift (Raymer §12.6 leading-edge-suction method, pp. 300-302):
K = S K100 + (1 - S) K0 with K0 = 1/CL_alpha and K100 = 1/(pi AR) subsonic,
rising linearly above M = 1 to meet K0 where the leading edge goes sonic
(Raymer Fig. 12.34). S is the leading-edge suction fraction.
"""
from __future__ import annotations

import numpy as np
from scipy.special import ellipe


def cla_subsonic(aspect_ratio, mach, sweep_tmax, s_exposed_ratio, fuselage_diameter, span, eta=0.95):
    beta2 = 1.0 - mach**2
    F = 1.07 * (1 + fuselage_diameter / span) ** 2
    a = aspect_ratio
    root = np.sqrt(4 + a**2 * beta2 / eta**2 * (1 + np.tan(sweep_tmax) ** 2 / beta2))
    return 2 * np.pi * a / (2 + root) * s_exposed_ratio * F


def cla_supersonic_delta(aspect_ratio, mach):
    beta = np.sqrt(mach**2 - 1.0)
    tan_eps = aspect_ratio / 4.0
    m = beta * tan_eps
    if m >= 1.0:
        return 4.0 / beta
    k2 = 1.0 - m**2  # scipy's ellipe takes the parameter m = k^2
    return 2 * np.pi * tan_eps / ellipe(k2)


def cl_alpha(aspect_ratio, mach, sweep_tmax, s_exposed_ratio, fuselage_diameter, span,
             m_sub=0.85, m_sup=1.2):
    """CL_alpha (1/rad) with a linear transonic bridge between m_sub and m_sup."""
    if mach <= m_sub:
        return cla_subsonic(aspect_ratio, mach, sweep_tmax, s_exposed_ratio, fuselage_diameter, span)
    if mach >= m_sup:
        return cla_supersonic_delta(aspect_ratio, mach)
    a = cla_subsonic(aspect_ratio, m_sub, sweep_tmax, s_exposed_ratio, fuselage_diameter, span)
    b = cla_supersonic_delta(aspect_ratio, m_sup)
    t = (mach - m_sub) / (m_sup - m_sub)
    return (1 - t) * a + t * b


def k_factor(aspect_ratio, mach, cla, sweep_le, suction):
    k0 = 1.0 / cla
    k100_sub = 1.0 / (np.pi * aspect_ratio)
    if mach <= 1.0:
        k100 = k100_sub
    else:
        m_le = 1.0 / np.cos(sweep_le)  # leading edge goes sonic
        if mach >= m_le:
            k100 = k0
        else:
            t = (mach - 1.0) / (m_le - 1.0)
            k100 = (1 - t) * k100_sub + t * k0
        k100 = min(k100, k0)
    return suction * k100 + (1 - suction) * k0
