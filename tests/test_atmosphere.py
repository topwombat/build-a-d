"""Method verification: our 1976 standard atmosphere against pyCycle's independent table model."""
import numpy as np
import openmdao.api as om
import pytest
from pycycle.elements.ambient import Ambient

from ssbj.core.atmosphere import FT, atmosphere


@pytest.mark.parametrize("alt_ft", [0.0, 15000.0, 36089.0, 50000.0, 60000.0, 65000.0])
def test_matches_pycycle(alt_ft):
    p = om.Problem(reports=False)
    p.model.add_subsystem("amb", Ambient(), promotes=["*"])
    p.setup()
    p.set_val("alt", alt_ft, units="ft")
    p.run_model()
    T, ps, rho, a, mu = atmosphere(alt_ft * FT)
    assert T == pytest.approx(float(p.get_val("Ts", units="degK")[0]), rel=2e-3)
    assert ps == pytest.approx(float(p.get_val("Ps", units="Pa")[0]), rel=3e-3)


def test_sea_level_defining_values():
    T, p, rho, a, mu = atmosphere(0.0)
    assert (T, p) == (288.15, 101325.0)
    assert rho == pytest.approx(101325.0 / (287.05287 * 288.15))


def test_out_of_range():
    with pytest.raises(ValueError):
        atmosphere(np.array([40000.0]))
