"""Method verification: the cruise integrator reproduces the Breguet range equation."""
import numpy as np
import pytest

from ssbj.core.atmosphere import FT, NMI, atmosphere
from ssbj.disciplines.mission.analysis import Mission
from ssbj.specs.schema import Mission as MissionSpec

LD, TSFC = 8.0, 1.2 / 3600.0  # 1/s


class ConstPolar:
    def cd(self, mach, alt_ft, cl, factors=None):
        return np.asarray(cl) / LD


class ConstDeck:
    count = 1

    def max_thrust(self, mach, alt_ft, reheat, factors=None):
        return 1e9

    def max_fuel_flow(self, mach, alt_ft, reheat, factors=None):
        return 1.0

    def fuel_flow_at_thrust(self, mach, alt_ft, thrust, factors=None):
        return thrust * TSFC / 9.80665, True


def _spec():
    return MissionSpec.model_validate({
        "payload": {"passengers": 0, "mass_per_passenger_kg": 1.0},
        "design_range_nmi": 1000.0,
        "cruise": {"mach": 2.0, "altitude_min_ft": 55000.0, "altitude_max_ft": 55000.0},
        "reserves": {"contingency_fraction_of_trip": 0.0, "diversion_nmi": 0.0, "diversion_mach": 0.5,
                     "diversion_altitude_ft": 0.0, "hold_minutes": 0.0, "hold_altitude_ft": 0.0,
                     "hold_mach": 0.3},
        "profile": [{"segment": "takeoff", "minutes": 1e-9}, {"segment": "cruise"}],
    })


def test_breguet():
    m = Mission(_spec(), ConstPolar(), ConstDeck(), 100.0)
    w0, fuel = 100000.0, 30000.0
    leg, _ = m._cruise(type("S", (), {"name": "c"})(), w0, fuel)
    v = 2.0 * atmosphere(55000 * FT)[3]
    breguet = v / TSFC * LD * np.log(w0 / (w0 - fuel)) / NMI
    assert leg.distance_nmi == pytest.approx(breguet, rel=1e-3)
