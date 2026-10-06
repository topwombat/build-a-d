"""Method verification for the area-rule wave drag (honesty rule 9)."""
import numpy as np
import pytest

from ssbj.disciplines.aero.wave_drag import (
    harris_wave_drag,
    sears_haack_area,
    sears_haack_drag,
    slender_body_drag,
)


@pytest.mark.parametrize("length,a_max", [(10.0, 1.0), (61.66, 7.5), (30.0, 0.3)])
def test_sears_haack_closed_form(length, a_max):
    """Raymer (1999) eq. 12.45 for the body of eq. 12.43, grid aligned with the body ends."""
    dx = length / 300
    x = np.arange(-25, 326) * dx
    assert slender_body_drag(x, sears_haack_area(x, length, a_max)) == pytest.approx(
        sears_haack_drag(length, a_max), rel=1e-6)


@pytest.mark.parametrize("n", [241, 401, 801])
def test_sears_haack_misaligned_grid(n):
    """With the body ends between grid points the error is O(dx / l): stated, not hidden."""
    x = np.linspace(-1.3, 11.7, n)
    err = slender_body_drag(x, sears_haack_area(x, 10.0, 1.0)) / sears_haack_drag(10.0, 1.0) - 1
    assert abs(err) < 2.0 * (x[1] - x[0]) / 10.0


def test_sears_haack_is_minimum():
    """Any other closed body of the same length and volume has more drag (Sears 1947)."""
    L = 10.0
    x = np.linspace(0, L, 801)
    sh = sears_haack_area(x, L, 1.0)
    vol = np.trapezoid(sh, x)
    parab = (1 - (2 * x / L - 1) ** 2) ** 2
    parab *= vol / np.trapezoid(parab, x)
    assert slender_body_drag(x, parab) > slender_body_drag(x, sh)


def test_scaling_with_length():
    """D/q scales as A_max^2 / l^2 for geometrically similar area distributions."""
    x1 = np.linspace(0, 10, 401)
    x2 = np.linspace(0, 20, 401)
    a1 = sears_haack_area(x1, 10, 1.0) + 0.3 * sears_haack_area(x1 * 2 - 5, 10, 1.0)
    a2 = sears_haack_area(x2, 20, 1.0) + 0.3 * sears_haack_area(x2 - 5, 10, 1.0)
    assert slender_body_drag(x2, a2) == pytest.approx(slender_body_drag(x1, a1) / 4, rel=1e-3)


def test_discretisation_converged(concorde_aircraft):
    """Default resolution is within 3 % of a much finer one (numerical error bar)."""
    base = harris_wave_drag(concorde_aircraft, 2.0)["D_q"]
    fine = harris_wave_drag(concorde_aircraft, 2.0, n_theta=48, n_x=961)["D_q"]
    assert base == pytest.approx(fine, rel=0.03)


def test_requires_supersonic(concorde_aircraft):
    with pytest.raises(ValueError):
        harris_wave_drag(concorde_aircraft, 0.9)
