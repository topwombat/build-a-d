import numpy as np
import pytest
from scipy.special import ellipe

from ssbj.disciplines.aero import friction as fr
from ssbj.disciplines.aero.lift import cla_supersonic_delta, k_factor


def test_turbulent_cf_value():
    # Raymer eq. 12.27 evaluated by hand at R = 1e7, M = 0: 0.455 / 7^2.58
    assert fr.cf_turbulent(1e7, 0.0) == pytest.approx(0.455 / 7**2.58)


def test_compressibility_lowers_cf():
    assert fr.cf_turbulent(1e8, 2.0) < fr.cf_turbulent(1e8, 0.5)


def test_cutoff_reynolds_limits_cf():
    # smooth vs rough: rough surface (large k) caps Re and raises Cf
    rough = fr.cf(50.0, 0.8, 1.2, 270.0, 1.8e-5, 1e-3)
    smooth = fr.cf(50.0, 0.8, 1.2, 270.0, 1.8e-5, 1e-7)
    assert rough > smooth


def test_delta_lift_limits():
    """Linear theory limits: slender-wing pi AR / 2 as beta -> 0; 4/beta at sonic LE."""
    ar = 1.8
    assert cla_supersonic_delta(ar, 1.0 + 1e-9) == pytest.approx(np.pi * ar / 2, rel=1e-3)
    m_sonic = np.sqrt(1 + (4 / ar) ** 2)
    assert cla_supersonic_delta(ar, m_sonic - 1e-6) == pytest.approx(4 / np.sqrt(m_sonic**2 - 1), rel=1e-3)
    assert cla_supersonic_delta(ar, m_sonic + 0.5) == pytest.approx(4 / np.sqrt((m_sonic + 0.5) ** 2 - 1))
    assert ellipe(0.0) == pytest.approx(np.pi / 2)


def test_k_bounds():
    cla = 2.0
    k = k_factor(1.8, 2.0, cla, np.radians(65), 0.2)
    assert 1 / (np.pi * 1.8) <= k <= 1 / cla
