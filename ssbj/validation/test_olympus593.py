"""Engine-deck validation against independent Olympus 593 Mk 610 data (item 1 of the roadmap).

Tolerances were fixed and committed BEFORE the two-spool model was run against these points
(see git history): each is 2 x the propulsion module's declared 1-sigma (prop.thrust 5 %,
prop.sfc 5 %), i.e. the model's own 95 % band. Airflow uses the thrust tolerance.

Validation targets (ssbj/validation/olympus593/sources.yaml; none is a model input):
  - net thrust per engine, M2.00 / 53,000 ft: 10,030 lbf (NASA TM-4144 Table II, pdf_read)
  - cruise TSFC: 1.19 /h (NASA TM-4144 p.2, pdf_read)
  - engine airflow, M2.0 / 55,000 ft: ~210 lb/s (Berger, AGARD CP-242 / NASA TM-75238 p.20-5)
The engine is defined from sea-level-static data only (dry and reheat thrust, airflow, OPR),
plus component efficiencies and losses (case provenance).
"""
import pytest

TOL_THRUST = 0.10
TOL_TSFC = 0.10
TOL_AIRFLOW = 0.10
LBF = 4.4482216152605
LBM = 0.45359237


@pytest.fixture(scope="module")
def olympus_point():
    from ssbj.disciplines.propulsion.two_spool import olympus_validation_point

    return olympus_validation_point()


def test_cruise_thrust(olympus_point):
    assert olympus_point["fn_N_M2_53k"] / LBF == pytest.approx(10030.0, rel=TOL_THRUST)


def test_cruise_tsfc(olympus_point):
    assert olympus_point["tsfc_per_h_M2_53k"] == pytest.approx(1.19, rel=TOL_TSFC)


def test_cruise_airflow(olympus_point):
    assert olympus_point["w_kg_s_M2_55k"] / LBM == pytest.approx(210.0, rel=TOL_AIRFLOW)
