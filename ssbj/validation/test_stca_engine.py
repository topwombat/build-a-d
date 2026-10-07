"""Turbofan cycle validation against the NASA 55t STCA engine (roadmap item 1, D-030).

Tolerances were fixed and committed BEFORE the turbofan model was run against these values (see git
history): 2 x the declared 1-sigma of the propulsion module (5 %), as for the Olympus checks.

Inputs (ssbj/validation/stca_engine/engine.yaml): the published design-point definition at M1.4 /
50,000 ft (thrust, fan PR, compressor PR, burner temperature, extraction ratio) plus generic
component efficiencies and cooling. Checked outputs (sources.yaml; none is an input):
  - specific fuel consumption 0.943 /h
  - bypass ratio 2.9 (follows from fan PR and extraction ratio)
  - compressor exit temperature 1,450 R
  - nozzle pressure ratio 5.9
  - engine-face corrected flow 413 lbm/s (sets specific thrust; the Olympus model failed on this)
The targets are NASA NPSS results, so this is model-to-model, not model-to-test.
"""
import pytest

TOL = 0.10


@pytest.fixture(scope="module")
def point():
    from ssbj.disciplines.propulsion.two_spool import stca_validation_point

    return stca_validation_point()


def test_thrust_is_the_input(point):
    assert point["fn_lbf"] == pytest.approx(3330.0, rel=1e-3)


def test_sfc(point):
    assert point["tsfc_per_h"] == pytest.approx(0.943, rel=TOL)


def test_bypass_ratio(point):
    assert point["bpr"] == pytest.approx(2.9, rel=TOL)


def test_compressor_exit_temperature(point):
    assert point["t3_R"] == pytest.approx(1450.0, rel=TOL)


def test_nozzle_pressure_ratio(point):
    assert point["npr"] == pytest.approx(5.9, rel=TOL)


def test_corrected_flow(point):
    assert point["wc2_lbm_s"] == pytest.approx(413.0, rel=TOL)
