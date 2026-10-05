"""Segment-by-segment mission integration.

Climb and acceleration segments use the energy method: along a straight path
in (Mach, altitude), each step's change in energy height divided by the
specific excess power Ps = (T - D) V / (W g) gives the time; fuel and
distance follow. Cruise is integrated in weight steps with thrust = drag;
the range-filling cruise flies the spec Mach at the altitude, within the
spec band, that maximises specific range at the current weight (cruise-climb).
The descent flies at idle along a straight (Mach, altitude) path.

Two entry points:
    fly_range(..., ramp_fuel)   -> range with the given fuel, reserves held back
    fly_distance(..., distance) -> fuel needed (trip, block, reserves) for a distance
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ssbj.core.atmosphere import FT, GAMMA, NMI, atmosphere
from ssbj.core.interface import DisciplineResult, Factors, Uncertainty, Validity

G = 9.80665
N_CLIMB = 40
N_CRUISE = 60

# Integration error is not sampled: halving or doubling the step counts changes range and fuel by
# <= 0.3 % on Concorde (tests/test_mission_convergence.py), well inside the other factors.
UNCERTAINTIES: list[Uncertainty] = []

LIMITS = [
    "Climb, acceleration and descent follow the prescribed straight (Mach, altitude) paths; no "
    "trajectory optimisation.",
    "Flight-path angle is neglected in lift (L = W) and in distance (cos gamma = 1).",
    "Descent at idle: idle thrust taken as zero, idle fuel flow scaled from the SLS taxi setting by "
    "ambient pressure ratio.",
    "Diversion flown as level cruise at the reserve Mach and altitude (no climb or descent).",
    "No winds, no temperature deviation from ISA, no air-traffic constraints.",
    "Centre-of-gravity and trim drag effects (fuel transfer for trim) are not modelled.",
    "Reserve detail (alternate distance, hold) is an assumption with no error factor; on Concorde the "
    "reserves are ~19 t and removing hold and diversion adds ~700 nmi of range.",
]


class MissionInfeasible(RuntimeError):
    pass


@dataclass
class Leg:
    name: str
    kind: str
    fuel_kg: float
    distance_nmi: float
    time_min: float
    w_start_kg: float
    w_end_kg: float
    detail: dict = field(default_factory=dict)


@dataclass
class Flight:
    legs: list[Leg]
    reserves_kg: float
    reserve_detail: dict
    transonic_margin: float  # min (T - D)/D over 0.9 <= M <= 1.3 on climb segments
    warnings: list[str]

    @property
    def trip_fuel_kg(self) -> float:
        return sum(l.fuel_kg for l in self.legs if l.kind != "taxi")

    @property
    def block_fuel_kg(self) -> float:
        return sum(l.fuel_kg for l in self.legs)

    @property
    def range_nmi(self) -> float:
        return sum(l.distance_nmi for l in self.legs)


class Mission:
    def __init__(self, spec, polar, deck, s_ref: float, factors: Factors | None = None):
        self.spec = spec
        self.polar = polar
        self.deck = deck
        self.s_ref = s_ref
        self.f = factors or Factors()
        self.warnings: list[str] = []
        self.fn_sls_dry_total = deck.max_thrust(0.0, 0.0, reheat=False)

    # ------------------------------------------------------------------ physics helpers
    def _drag(self, mach, alt_ft, w_kg):
        T, p, rho, a, mu = atmosphere(alt_ft * FT)
        q = 0.5 * GAMMA * p * mach**2
        cl = w_kg * G / (q * self.s_ref)
        cd = float(self.polar.cd(mach, alt_ft, cl, self.f))
        return q * self.s_ref * cd, cl, mach * a

    def _cruise_ff(self, mach, alt_ft, w_kg):
        d, cl, v = self._drag(mach, alt_ft, w_kg)
        ff, ok = self.deck.fuel_flow_at_thrust(mach, alt_ft, d, self.f)
        return ff, v, d, cl, ok

    def _idle_ff(self, alt_ft):
        p_ratio = atmosphere(alt_ft * FT)[1] / atmosphere(0.0)[1]
        return self.idle_ff_sls * p_ratio

    @property
    def idle_ff_sls(self):
        taxi = next((s for s in self.spec.profile if s.segment == "taxi"), None)
        frac = taxi.thrust_fraction_of_sls_dry if taxi else 0.05
        return self.deck.fuel_flow_at_thrust(0.0, 0.0, frac * self.fn_sls_dry_total, self.f)[0]

    # ------------------------------------------------------------------ segments
    def _taxi(self, s, w):
        fuel = s.minutes * 60 * self.idle_ff_sls
        return Leg(s.name, "taxi", fuel, 0.0, s.minutes, w, w - fuel)

    def _takeoff(self, s, w):
        ff = self.deck.max_fuel_flow(0.2, 0.0, reheat=(s.power == "max_reheat"), factors=self.f)
        fuel = s.minutes * 60 * ff
        return Leg(s.name, "takeoff", fuel, 0.0, s.minutes, w, w - fuel), (s.end_mach, s.end_altitude_ft)

    def _climb(self, s, w, state, margins):
        m0, h0 = state
        m1, h1 = s.to_mach, s.to_altitude_ft
        reheat = s.power == "max_reheat"
        fuel = dist = time = 0.0
        w0 = w
        ms = np.linspace(m0, m1, N_CLIMB + 1)
        hs = np.linspace(h0, h1, N_CLIMB + 1)
        min_ps = np.inf
        for i in range(N_CLIMB):
            mm, hm = 0.5 * (ms[i] + ms[i + 1]), 0.5 * (hs[i] + hs[i + 1])
            a0 = atmosphere(hs[i] * FT)[3]
            a1 = atmosphere(hs[i + 1] * FT)[3]
            v0, v1 = ms[i] * a0, ms[i + 1] * a1
            dhe = (hs[i + 1] - hs[i]) * FT + (v1**2 - v0**2) / (2 * G)
            d, cl, v = self._drag(mm, hm, w)
            t = self.deck.max_thrust(mm, hm, reheat, self.f)
            ff = self.deck.max_fuel_flow(mm, hm, reheat, self.f)
            if 0.9 <= mm <= 1.3:
                margins.append((t - d) / d)
            ps = (t - d) * v / (w * G)
            min_ps = min(min_ps, ps)
            if ps <= 0:
                raise MissionInfeasible(
                    f"{s.name}: no excess power at M {mm:.2f}, {hm:.0f} ft (T = {t / 1000:.1f} kN, "
                    f"D = {d / 1000:.1f} kN)")
            dt = max(dhe, 0.0) / ps
            fuel += ff * dt
            w -= ff * dt
            dist += v * dt
            time += dt
        return Leg(s.name, "climb", fuel, dist / NMI, time / 60, w0, w,
                   {"min_specific_excess_power_m_s": min_ps, "power": s.power}), (m1, h1)

    def _cruise_fixed(self, s, w, n=N_CRUISE):
        ds = s.distance_nmi * NMI / n
        fuel = time = 0.0
        w0 = w
        for _ in range(n):
            ff, v, d, cl, ok = self._cruise_ff(s.mach, s.altitude_ft, w)
            if not ok:
                raise MissionInfeasible(f"{s.name}: thrust required exceeds max dry thrust")
            dt = ds / v
            fuel += ff * dt
            w -= ff * dt
            time += dt
        return Leg(s.name, "cruise_fixed", fuel, s.distance_nmi, time / 60, w0, w), (s.mach, s.altitude_ft)

    def _best_altitude(self, w):
        c = self.spec.cruise
        if c.mode == "constant_altitude":
            return c.altitude_min_ft
        hs = np.linspace(c.altitude_min_ft, c.altitude_max_ft, 11)
        best, best_sr = hs[0], -1.0
        for h in hs:
            ff, v, d, cl, ok = self._cruise_ff(c.mach, h, w)
            if ok and v / ff > best_sr:
                best, best_sr = h, v / ff
        if best_sr < 0:
            raise MissionInfeasible("cruise: thrust required exceeds max dry thrust at every altitude in the band")
        return best

    def _cruise(self, s, w, fuel_to_burn, n=N_CRUISE):
        c = self.spec.cruise
        if fuel_to_burn <= 0:
            raise MissionInfeasible("no fuel left for the range-filling cruise")
        dw = fuel_to_burn / n
        dist = time = 0.0
        w0 = w
        alts, lds, tsfcs = [], [], []
        for _ in range(n):
            wm = w - 0.5 * dw
            h = self._best_altitude(wm)
            ff, v, d, cl, ok = self._cruise_ff(c.mach, h, wm)
            dt = dw / ff
            dist += v * dt
            time += dt
            w -= dw
            alts.append(h)
            lds.append(wm * G / d)
            tsfcs.append(ff * G / d * 3600.0)
        return Leg(s.name, "cruise", fuel_to_burn, dist / NMI, time / 60, w0, w,
                   {"altitude_start_ft": alts[0], "altitude_end_ft": alts[-1],
                    "l_over_d_mean": float(np.mean(lds)), "tsfc_mean_per_h": float(np.mean(tsfcs))}), (c.mach, alts[-1])

    def _descent(self, s, w, state):
        m0, h0 = state
        ms = np.linspace(m0, s.to_mach, N_CLIMB + 1)
        hs = np.linspace(h0, s.to_altitude_ft, N_CLIMB + 1)
        fuel = dist = time = 0.0
        w0 = w
        for i in range(N_CLIMB):
            mm, hm = 0.5 * (ms[i] + ms[i + 1]), 0.5 * (hs[i] + hs[i + 1])
            v0 = ms[i] * atmosphere(hs[i] * FT)[3]
            v1 = ms[i + 1] * atmosphere(hs[i + 1] * FT)[3]
            dhe = (hs[i] - hs[i + 1]) * FT + (v0**2 - v1**2) / (2 * G)  # energy lost (> 0)
            d, cl, v = self._drag(mm, hm, w)
            if s.lift_to_drag_glide:
                d = w * G / s.lift_to_drag_glide
            dt = max(dhe, 0.0) * w * G / (d * v)  # idle thrust ~ 0: -Ps = D V / (W g)
            ff = self._idle_ff(hm)
            fuel += ff * dt
            w -= ff * dt
            dist += v * dt
            time += dt
        return Leg(s.name, "descent", fuel, dist / NMI, time / 60, w0, w), (s.to_mach, s.to_altitude_ft)

    def reserves(self, w_land, trip_fuel):
        r = self.spec.reserves
        cont = r.contingency_fraction_of_trip * trip_fuel
        # diversion: level cruise at the reserve condition
        div_leg, _ = self._cruise_fixed(type("S", (), {"name": "diversion", "distance_nmi": r.diversion_nmi,
                                                        "mach": r.diversion_mach,
                                                        "altitude_ft": r.diversion_altitude_ft})(),
                                        w_land, n=10)
        w = w_land - div_leg.fuel_kg
        ff, v, d, cl, ok = self._cruise_ff(r.hold_mach, r.hold_altitude_ft, w)
        hold = ff * r.hold_minutes * 60
        return cont + div_leg.fuel_kg + hold, {"contingency_kg": cont, "diversion_kg": div_leg.fuel_kg,
                                               "hold_kg": hold}

    # ------------------------------------------------------------------ whole mission
    def _fly(self, w_ramp, cruise_fuel):
        legs = []
        margins: list[float] = []
        w = w_ramp
        state = (0.0, 0.0)
        for s in self.spec.profile:
            k = s.segment
            if k == "taxi":
                leg = self._taxi(s, w)
            elif k == "takeoff":
                leg, state = self._takeoff(s, w)
            elif k == "climb":
                leg, state = self._climb(s, w, state, margins)
            elif k == "cruise_fixed":
                leg, state = self._cruise_fixed(s, w)
            elif k == "cruise":
                leg, state = self._cruise(s, w, cruise_fuel)
            elif k == "descent":
                leg, state = self._descent(s, w, state)
            else:  # pragma: no cover
                raise ValueError(k)
            legs.append(leg)
            w = leg.w_end_kg
        return legs, (min(margins) if margins else float("nan"))

    def fly_range(self, w_ramp: float, ramp_fuel: float) -> Flight:
        """Range with ``ramp_fuel`` aboard at ramp weight ``w_ramp``, landing with full reserves."""
        cruise_fuel = 0.6 * ramp_fuel
        for _ in range(30):
            legs, margin = self._fly(w_ramp, cruise_fuel)
            used = sum(l.fuel_kg for l in legs)
            trip = sum(l.fuel_kg for l in legs if l.kind != "taxi")
            res, rd = self.reserves(legs[-1].w_end_kg, trip)
            err = ramp_fuel - used - res
            if abs(err) < 0.5:
                break
            cruise_fuel += err / (1.0 + self.spec.reserves.contingency_fraction_of_trip)
            if cruise_fuel <= 0:
                raise MissionInfeasible("fuel does not cover the non-cruise segments and reserves")
        else:
            raise MissionInfeasible(f"range iteration did not converge (fuel error {err:.1f} kg)")
        return Flight(legs, res, rd, margin, list(self.warnings))

    def fly_distance(self, w_zero_fuel: float, distance_nmi: float, fuel_capacity: float) -> tuple[Flight, float]:
        """Fuel load needed to fly ``distance_nmi`` with reserves; returns (flight, ramp fuel).

        Searched between 20 % and 100 % of the fuel capacity. A fuel load too small to cover the fixed segments
        counts as zero range; any other infeasibility (e.g. no excess power when heavy) is raised.
        Secant first, bisection if the secant leaves the bracket.
        """

        def short(fuel):
            try:
                return self.fly_range(w_zero_fuel + fuel, fuel).range_nmi - distance_nmi
            except MissionInfeasible as e:
                if "does not cover" in str(e) or "no fuel left" in str(e):
                    return -distance_nmi
                raise

        # Bounded by the tanks: beyond ~capacity range is non-monotonic in fuel (the heavy supersonic
        # climb collapses), so extrapolating past it gave spurious answers (D-022).
        lo, hi = 0.2 * fuel_capacity, fuel_capacity
        f_lo = short(lo)
        # the heaviest loads may be unflyable (no excess power): bisect for the heaviest flyable load
        # (a heavy load whose climb burns all the fuel also counts as unflyable here)
        def flyable(x):
            try:
                fx = short(x)
            except MissionInfeasible:
                return None
            return None if fx <= -distance_nmi else fx

        f_hi = flyable(hi)
        if f_hi is None:
            ok, bad = lo, hi
            for _ in range(20):
                mid = 0.5 * (ok + bad)
                f_mid = flyable(mid)
                if f_mid is not None:
                    ok, f_ok = mid, f_mid
                else:
                    bad = mid
                if bad - ok < 1.0:
                    break
            if ok == lo:
                raise MissionInfeasible("no flyable fuel load above the lower bracket") from None
            hi, f_hi = ok, f_ok
        if f_lo > 0:
            lo, f_lo = 0.02 * fuel_capacity, short(0.02 * fuel_capacity)
        if f_hi < 0:
            raise MissionInfeasible(f"design range not reachable within the fuel capacity: the heaviest "
                                    f"flyable load ({hi:.0f} kg) falls short by {-f_hi:.0f} nmi")
        x = lo + (hi - lo) * (-f_lo) / (f_hi - f_lo)
        for _ in range(60):
            fx = short(x)
            if abs(fx) < 0.5 or hi - lo < 1.0:
                break
            if fx < 0:
                lo, f_lo = x, fx
            else:
                hi, f_hi = x, fx
            x_sec = lo + (hi - lo) * (-f_lo) / (f_hi - f_lo)
            x = x_sec if lo < x_sec < hi and f_lo > -distance_nmi else 0.5 * (lo + hi)
        else:
            raise MissionInfeasible("fuel-for-distance search did not converge")
        return self.fly_range(w_zero_fuel + x, x), x


def analyse(spec, polar, deck, s_ref, oew_kg, mtow_kg, fuel_capacity_kg, factors=None) -> DisciplineResult:
    """Run the max-fuel range mission and the design-distance mission independently.

    Each result is either the mission record or ``{"infeasible": reason}``; one failing does
    not discard the other.
    """
    validity = Validity("mission", list(LIMITS))
    m = Mission(spec, polar, deck, s_ref, factors)
    payload = spec.payload.mass_kg
    zfw = oew_kg + payload
    ramp_fuel = min(fuel_capacity_kg, mtow_kg - zfw)
    out: dict = {"zfw_kg": zfw, "payload_kg": payload}
    if ramp_fuel <= 0:
        raise MissionInfeasible("OEW + payload exceeds MTOW")
    if ramp_fuel < mtow_kg - zfw:
        validity.warn("range is volume-limited: fuel capacity reached before MTOW")
    try:
        fr = m.fly_range(zfw + ramp_fuel, ramp_fuel)
        cruise = next(l for l in fr.legs if l.kind == "cruise")
        out["range"] = {"ramp_fuel_kg": ramp_fuel, "range_nmi": fr.range_nmi, "trip_fuel_kg": fr.trip_fuel_kg,
                        "block_fuel_kg": fr.block_fuel_kg, "reserves_kg": fr.reserves_kg,
                        "reserve_detail": fr.reserve_detail, "transonic_thrust_margin": fr.transonic_margin,
                        "ld_cruise": cruise.detail["l_over_d_mean"],
                        "tsfc_cruise_per_h": cruise.detail["tsfc_mean_per_h"],
                        "legs": [l.__dict__ for l in fr.legs], "tow_kg": zfw + ramp_fuel - fr.legs[0].fuel_kg}
    except MissionInfeasible as e:
        out["range"] = {"infeasible": str(e)}
        validity.warn(f"max-fuel range mission infeasible: {e}")
    try:
        fd, fuel = m.fly_distance(zfw, spec.design_range_nmi, fuel_capacity_kg)
        out["design_mission"] = {"distance_nmi": spec.design_range_nmi, "ramp_fuel_kg": fuel,
                                 "trip_fuel_kg": fd.trip_fuel_kg, "block_fuel_kg": fd.block_fuel_kg,
                                 "reserves_kg": fd.reserves_kg, "tow_kg": zfw + fuel - fd.legs[0].fuel_kg,
                                 "legs": [l.__dict__ for l in fd.legs],
                                 "transonic_thrust_margin": fd.transonic_margin}
        if fuel > fuel_capacity_kg:
            validity.warn("design mission needs more fuel than the tanks hold")
        if zfw + fuel > mtow_kg:
            validity.warn("design mission takeoff weight exceeds MTOW")
    except MissionInfeasible as e:
        out["design_mission"] = {"infeasible": str(e)}
        validity.warn(f"design-distance mission infeasible: {e}")
    validity.warnings += m.warnings
    return DisciplineResult("mission", "energy-method climb, cruise-climb, idle descent", out,
                            UNCERTAINTIES, validity)
