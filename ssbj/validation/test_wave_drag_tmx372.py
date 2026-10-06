"""Wave-drag validation against a public wind-tunnel test: NASA TM X-372 arrow model (item 1).

Tolerance fixed and committed BEFORE the comparison was computed (see git history):
2 x the aero module's declared 1-sigma for wave drag (aero.wave = 25 %), i.e. +/- 50 %, at each
Mach point. The experimental values INCLUDE the blunt-trailing-edge wing base drag (the report
says so); a far-field area-rule code with the base step in the area distribution is compared to
them as published. The report's own area-rule theory (49 harmonics) is a code-to-code diagnostic,
not a gate. Geometry and data: ssbj/validation/wave_drag/tmx372_arrow_geometry.yaml.
"""
import pytest

TOL = 0.50
POINTS = [1.55, 1.70, 2.00, 2.35, 3.00]


@pytest.fixture(scope="module")
def results():
    from ssbj.validation.wave_drag.tmx372 import compare

    return compare(POINTS)


@pytest.mark.parametrize("mach", POINTS)
def test_against_experiment(results, mach):
    r = results[mach]
    assert r["model_cd"] == pytest.approx(r["exp_cd"], rel=TOL)
