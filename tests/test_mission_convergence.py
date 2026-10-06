"""Numerical checks of the mission integrator on the Concorde case (uses the committed caches)."""
import pytest

from ssbj.disciplines.aero.polar import build_polar
from ssbj.disciplines.mission import analysis
from ssbj.disciplines.propulsion.two_spool import build_two_spool


@pytest.fixture(scope="module")
def setup(concorde_case, concorde_aircraft):
    polar = build_polar(concorde_aircraft).outputs["polar"]
    deck = build_two_spool(concorde_case.design.engine).outputs["deck"]
    zfw = 72000.0 + concorde_case.mission.payload.mass_kg
    return concorde_case, polar, deck, concorde_aircraft.s_ref, zfw


def _range(setup, n_climb, n_cruise, monkeypatch):
    case, polar, deck, s_ref, zfw = setup
    monkeypatch.setattr(analysis, "N_CLIMB", n_climb)
    monkeypatch.setattr(analysis, "N_CRUISE", n_cruise)
    m = analysis.Mission(case.mission, polar, deck, s_ref)
    fuel = case.design.weights.fuel_capacity_kg
    return m.fly_range(zfw + fuel, fuel).range_nmi


def test_step_halving(setup, monkeypatch):
    """Integration error behind the decision not to sample one (UNCERTAINTIES is empty)."""
    base = _range(setup, 40, 60, monkeypatch)
    fine = _range(setup, 80, 120, monkeypatch)
    assert base == pytest.approx(fine, rel=0.005)


def test_fuel_for_distance_inverts_range(setup):
    case, polar, deck, s_ref, zfw = setup
    m = analysis.Mission(case.mission, polar, deck, s_ref)
    flight, fuel = m.fly_distance(zfw, 3000.0, case.design.weights.fuel_capacity_kg)
    assert flight.range_nmi == pytest.approx(3000.0, abs=1.0)
    again = m.fly_range(zfw + fuel, fuel)
    assert again.range_nmi == pytest.approx(3000.0, abs=1.0)
    # ramp fuel = block fuel + reserves
    assert again.block_fuel_kg + again.reserves_kg == pytest.approx(fuel, abs=1.0)
