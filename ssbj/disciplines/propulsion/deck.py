"""Engine deck: installed thrust and fuel flow vs Mach, altitude and power setting.

Generated from the pyCycle afterburning turbojet in cycle.py, swept over a
(Mach, altitude) grid with dry power settings (fractions of T4_max) and one
full-reheat setting. Points are solved with continuation along altitude;
points that fail to converge are recorded and filled from the nearest
converged altitude in the same Mach row (and flagged).

Installation: inlet total-pressure recovery follows the MIL-E-5008B standard
schedule (1.0 for M <= 1; 1 - 0.075 (M - 1)^1.35 above), the reference Raymer
(1999) App. A.4 cites for its installed engine data. Nozzle losses are the
pyCycle velocity coefficient Cv. Spillage, bleed and boat-tail drag are not
modelled (see docs/known_limits.md).

Engine weight and size: Raymer (1999) eqs. 10.1-10.3 scaled from the
afterburning engine of Raymer App. A.4-1 (30,000 lbf SLS max thrust,
3,000 lb, 160 in long, 44 in diameter).
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import time
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ssbj.core.atmosphere import FT, LBF, LBM
from ssbj.core.interface import DisciplineResult, Factors, Uncertainty, Validity

MACH = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2])
ALT_FT = np.array([0, 5000, 10000, 15000, 20000, 25000, 30000, 36089, 40000, 45000, 50000,
                   55000, 60000, 65000], dtype=float)
T4_FRACS = np.array([1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65])

CACHE_DIR = Path(os.environ.get("SSBJ_DECK_CACHE", Path(__file__).parent / "decks"))

# Raymer (1999) App. A.4-1, afterburning turbofan reference engine
REF_ENGINE = {"thrust_lbf": 30000.0, "weight_lb": 3000.0, "length_in": 160.0, "diameter_in": 44.0}

UNCERTAINTIES = [
    Uncertainty("prop.thrust", 0.05,
                "Single-spool cycle with generic AXI5/LPT2269 maps standing in for the real "
                "engine; installation drags not modelled.", "available thrust, all settings"),
    Uncertainty("prop.sfc", 0.05,
                "Component efficiencies are assumed; generic maps; no Reynolds or bleed effects.",
                "fuel flow at given thrust"),
    Uncertainty("prop.weight", 0.30,
                "Scaled from Raymer's 1990s-technology reference engine (bypass 0.41); a 1960s "
                "turbojet is expected to be heavier, so this is biased low by an unknown amount.",
                "engine dry weight"),
]

LIMITS = [
    "Single-spool turbojet stands in for twin-spool engines; part-power matching is approximate.",
    "Generic compressor and turbine maps (pyCycle AXI5, LPT2269) scaled to the design point.",
    "No mechanical-speed or T2 limit schedule: only T4 is limited.",
    "Inlet recovery is the MIL-E-5008B standard schedule, not a designed intake.",
    "Spillage, bypass, bleed and nozzle boat-tail drag are not modelled.",
    "Idle and descent fuel flow are extrapolated below 65 % of T4_max.",
]


def ram_recovery(mach):
    m = np.asarray(mach, dtype=float)
    return np.where(m <= 1.0, 1.0, 1.0 - 0.075 * np.clip(m - 1.0, 0, None) ** 1.35)


Q_MAX_PA = 1.2e5  # ~2,500 psf: points above this dynamic pressure are outside any SST envelope


def in_envelope(mach: float, alt_ft: float) -> bool:
    """Deck points worth solving: dynamic pressure below Q_MAX_PA, no very slow high-altitude points."""
    from ssbj.core.atmosphere import GAMMA, atmosphere

    p = atmosphere(alt_ft * FT)[1]
    q = 0.5 * GAMMA * p * mach**2
    if q > Q_MAX_PA:
        return False
    if mach < 0.35 and alt_ft > 20000:
        return False
    if mach < 0.75 and alt_ft > 45000:
        return False
    return True


def _cycle_source_hash() -> str:
    src = (Path(__file__).parent / "cycle.py").read_bytes() + Path(__file__).read_bytes()
    return hashlib.sha256(src).hexdigest()[:12]


def deck_key(engine) -> str:
    blob = json.dumps({"engine": engine.model_dump(), "mach": MACH.tolist(), "alt": ALT_FT.tolist(),
                       "t4": T4_FRACS.tolist(), "src": _cycle_source_hash()}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------- generation
def _new_problem(engine):
    import openmdao.api as om

    from ssbj.disciplines.propulsion.cycle import DesignPlusOffDesign

    p = om.Problem(reports=False)
    p.model = DesignPlusOffDesign()
    p.setup()
    for pt in ("DESIGN", "OD"):
        p.model._get_subsystem(pt).nonlinear_solver.options["err_on_non_converge"] = True
    p.set_val("DESIGN.fc.alt", 0.0, units="ft")
    p.set_val("DESIGN.fc.MN", 1e-6)
    p.set_val("DESIGN.balance.rhs:W", engine.fn_sls_dry_kN, units="kN")
    p.set_val("DESIGN.balance.rhs:FAR", engine.t4_max_K, units="degK")
    p.set_val("DESIGN.comp.PR", engine.opr)
    p.set_val("DESIGN.comp.eff", engine.comp_eff)
    p.set_val("DESIGN.turb.eff", engine.turb_eff)
    p.set_val("DESIGN.nozz.Cv", engine.nozzle_cv)
    p.set_val("OD.nozz.Cv", engine.nozzle_cv)
    w_guess = engine.fn_sls_dry_kN * 1000 / LBF / 80.0  # ~80 lbf per lbm/s for a dry turbojet
    p["DESIGN.balance.FAR"] = 0.02
    p["DESIGN.balance.W"] = w_guess
    p["DESIGN.balance.turb_PR"] = 4.0
    p["DESIGN.fc.balance.Pt"] = 14.6959
    p["DESIGN.fc.balance.Tt"] = 518.67
    p.set_val("OD.fc.MN", 1e-6)
    p.set_val("OD.fc.alt", 0.0, units="ft")
    p.set_val("OD.balance.rhs:FAR", engine.t4_max_K, units="degK")
    p["OD.balance.W"] = w_guess
    p["OD.balance.FAR"] = 0.02
    p["OD.balance.Nmech"] = 8070.0
    p["OD.turb.PR"] = 4.0
    p.set_solver_print(level=-1)
    return p


_GUESS_KEYS = ["balance.W", "balance.FAR", "balance.Nmech", "turb.PR"]


def _solve_row(args):
    """Solve all altitudes and power settings for one Mach number (runs in a worker process)."""
    engine, mach = args
    warnings.filterwarnings("ignore")
    p = _new_problem(engine)
    p.run_model()  # design point + SLS checks
    design = {k: p.get_val(f"DESIGN.{k}").copy() for k in ("balance.W", "balance.FAR", "balance.turb_PR")}
    sls = {"W_lbm_s": float(p.get_val("DESIGN.inlet.Fl_O:stat:W", units="lbm/s")[0])}
    out_vec = p.model._outputs.asarray()
    seed = out_vec.copy()  # full converged state at SLS; restored whenever a solve fails
    n_alt, n_t4 = len(ALT_FT), len(T4_FRACS)
    fn = np.full((n_alt, n_t4 + 1), np.nan)
    ff = np.full((n_alt, n_t4 + 1), np.nan)
    state = {"last": seed.copy()}

    cur = {"mach": 1e-6}

    def solve(h, frac, ab_far=0.0):
        for guess in (state["last"], seed):
            # restore the full state first: auto-IVC outputs (the inputs below) live in it too
            out_vec[:] = guess
            p.set_val("OD.fc.MN", max(cur["mach"], 1e-6))
            p.set_val("OD.inlet.ram_recovery", float(ram_recovery(cur["mach"])))
            p.set_val("OD.fc.alt", h, units="ft")
            p.set_val("OD.balance.rhs:FAR", engine.t4_max_K * frac, units="degK")
            p.set_val("OD.ab.Fl_I:FAR", ab_far)
            try:
                p.run_model()
            except Exception:
                continue
            if not np.all(np.isfinite(out_vec)):
                continue
            state["last"] = out_vec.copy()
            return True
        out_vec[:] = state["last"]
        return False

    def read():
        f = float(p.get_val("OD.perf.Fn", units="N")[0])
        w = float(p.get_val("OD.perf.Wfuel", units="kg/s")[0])
        return (f, w) if f > 0 and np.isfinite(w) else (np.nan, np.nan)

    def t_ab():
        return float(p.get_val("OD.ab.Fl_O:tot:T", units="degK")[0]) - engine.t_ab_K

    def reheat(h):
        """Ramp, then secant-iterate, the afterburner FAR to reach t_ab_K at T4_max."""
        x_prev, t_prev = 0.0, t_ab()  # current state is the dry full-power point
        x, t = x_prev, t_prev
        while t < 0:  # ramp in steps of 0.005 until the target temperature is bracketed
            x_prev, t_prev = x, t
            x = round(x + 0.005, 4)
            if x > 0.06 or not solve(h, 1.0, x):
                return np.nan, np.nan
            t = t_ab()
        x0, t0, x1, t1 = x_prev, t_prev, x, t
        for _ in range(8):
            if abs(t1) < 2.0 or t1 == t0:
                break
            x0, x1, t0 = x1, float(np.clip(x1 - t1 * (x1 - x0) / (t1 - t0), 1e-4, 0.06)), t1
            if not solve(h, 1.0, x1):
                return np.nan, np.nan
            t1 = t_ab()
        return read() if abs(t1) < 10.0 else (np.nan, np.nan)

    # continuation from the converged SLS state to a flyable start point for this Mach number
    h_start = float(np.interp(mach, [0.0, 0.9, 1.4, 2.0, 2.4], [0.0, 25000.0, 40000.0, 50000.0, 55000.0]))
    for t in np.linspace(0.0, 1.0, 9)[1:]:
        cur["mach"] = mach * t
        solve(h_start * t, 1.0)

    i0 = int(np.argmin(np.abs(ALT_FT - h_start)))
    start_state = None
    for order in (range(i0, n_alt), range(i0 - 1, -1, -1)):
        if start_state is not None:
            state["last"] = start_state.copy()
        for i in order:
            h = ALT_FT[i]
            if not in_envelope(mach, h):
                continue
            for j in range(n_t4):
                if solve(h, T4_FRACS[j]):
                    fn[i, j], ff[i, j] = read()
                    if j == 0:
                        full = state["last"].copy()
                        if i == i0:
                            start_state = full.copy()
            if np.isfinite(fn[i, 0]):
                state["last"] = full
                if solve(h, 1.0):
                    fn[i, n_t4], ff[i, n_t4] = reheat(h)
                state["last"] = full
    return mach, fn, ff, sls, {k: v.tolist() for k, v in design.items()}


def generate(engine, processes: int | None = None) -> dict:
    t0 = time.perf_counter()
    procs = processes or min(4, os.cpu_count() or 1)
    jobs = [(engine, float(m)) for m in MACH]
    if procs > 1:
        with mp.get_context("spawn").Pool(procs) as pool:
            rows = pool.map(_solve_row, jobs)
    else:
        rows = [_solve_row(j) for j in jobs]
    rows.sort(key=lambda r: r[0])
    fn = np.stack([r[1] for r in rows])  # (mach, alt, setting)
    ff = np.stack([r[2] for r in rows])
    return {"fn_N": fn.tolist(), "ff_kg_s": ff.tolist(), "sls": rows[0][3], "design": rows[0][4],
            "wall_time_s": time.perf_counter() - t0}


def load_or_generate(engine, processes: int | None = None) -> tuple[dict, str, bool]:
    key = deck_key(engine)
    path = CACHE_DIR / f"deck_{key}.json"
    if path.exists():
        return json.loads(path.read_text()), key, True
    raw = generate(engine, processes)
    raw["key"] = key
    raw["engine"] = engine.model_dump()
    raw["grid"] = {"mach": MACH.tolist(), "alt_ft": ALT_FT.tolist(), "t4_fracs": T4_FRACS.tolist()}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw))
    return raw, key, False


# ----------------------------------------------------------------------------- queries
@dataclass
class EngineDeck:
    fn: np.ndarray  # (n_mach, n_alt, n_set) N per engine; last setting is full reheat
    ff: np.ndarray  # kg/s per engine
    count: int
    filled: np.ndarray  # bool mask of points filled from neighbours

    @classmethod
    def from_raw(cls, raw: dict, count: int):
        fn = np.array(raw["fn_N"], dtype=float)
        ff = np.array(raw["ff_kg_s"], dtype=float)
        filled = ~np.isfinite(fn)
        for i in range(fn.shape[0]):
            for k in range(fn.shape[2]):
                good = np.isfinite(fn[i, :, k])
                if not good.any():
                    continue
                idx = np.where(good)[0]
                for j in np.where(~good)[0]:
                    jj = idx[np.argmin(np.abs(idx - j))]
                    # scale with ambient pressure ratio from the nearest converged altitude
                    from ssbj.core.atmosphere import atmosphere

                    pr = atmosphere(ALT_FT[j] * FT)[1] / atmosphere(ALT_FT[jj] * FT)[1]
                    fn[i, j, k] = fn[i, jj, k] * pr
                    ff[i, j, k] = ff[i, jj, k] * pr
        return cls(fn, ff, count, filled)

    def _bilinear(self, arr, mach, alt_ft):
        im = int(np.clip(np.searchsorted(MACH, mach) - 1, 0, len(MACH) - 2))
        ia = int(np.clip(np.searchsorted(ALT_FT, alt_ft) - 1, 0, len(ALT_FT) - 2))
        tm = np.clip((mach - MACH[im]) / (MACH[im + 1] - MACH[im]), 0, 1)
        ta = np.clip((alt_ft - ALT_FT[ia]) / (ALT_FT[ia + 1] - ALT_FT[ia]), 0, 1)
        return ((1 - tm) * (1 - ta) * arr[im, ia] + tm * (1 - ta) * arr[im + 1, ia]
                + (1 - tm) * ta * arr[im, ia + 1] + tm * ta * arr[im + 1, ia + 1])

    def max_thrust(self, mach, alt_ft, reheat: bool, factors: Factors | None = None) -> float:
        f = factors or Factors()
        k = -1 if reheat else 0
        return float(self._bilinear(self.fn[..., k], mach, alt_ft)) * self.count * f("prop.thrust")

    def max_fuel_flow(self, mach, alt_ft, reheat: bool, factors: Factors | None = None) -> float:
        f = factors or Factors()
        k = -1 if reheat else 0
        return float(self._bilinear(self.ff[..., k], mach, alt_ft)) * self.count * f("prop.sfc") * f("prop.thrust")

    def fuel_flow_at_thrust(self, mach, alt_ft, thrust_total, factors: Factors | None = None) -> tuple[float, bool]:
        """Total fuel flow (kg/s) to produce ``thrust_total`` (N) dry; returns (ff, feasible)."""
        f = factors or Factors()
        fn = self._bilinear(self.fn[..., :-1], mach, alt_ft) * self.count * f("prop.thrust")
        ff = self._bilinear(self.ff[..., :-1], mach, alt_ft) * self.count * f("prop.thrust")
        order = np.argsort(fn)
        fn, ff = fn[order], ff[order]
        feasible = thrust_total <= fn[-1] * (1 + 1e-9)
        if thrust_total >= fn[0]:
            w = float(np.interp(thrust_total, fn, ff))
        else:  # below the lowest computed setting: linear extrapolation, floor at 30 % of lowest
            slope = (ff[1] - ff[0]) / (fn[1] - fn[0])
            w = max(ff[0] + slope * (thrust_total - fn[0]), 0.3 * ff[0])
        return w * f("prop.sfc"), bool(feasible)


def engine_weight_and_size(fn_sls_max_N: float) -> dict:
    sf = (fn_sls_max_N / LBF) / REF_ENGINE["thrust_lbf"]
    return {
        "scale_factor": sf,
        "dry_weight_kg": REF_ENGINE["weight_lb"] * sf**1.1 * LBM,  # Raymer eq. 10.3
        "length_m": REF_ENGINE["length_in"] * sf**0.4 * 0.0254,  # eq. 10.1
        "diameter_m": REF_ENGINE["diameter_in"] * sf**0.5 * 0.0254,  # eq. 10.2
    }


def build_engine(engine, processes: int | None = None) -> DisciplineResult:
    raw, key, cached = load_or_generate(engine, processes)
    deck = EngineDeck.from_raw(raw, engine.count)
    validity = Validity("propulsion", list(LIMITS))
    n_fill = int(deck.filled.sum())
    if n_fill:
        validity.warn(f"{n_fill} of {deck.filled.size} deck points did not converge and were filled "
                      "from the nearest converged altitude (pressure-ratio scaling)")
    fn_sls_dry = float(deck.fn[0, 0, 0])
    fn_sls_wet = float(deck.fn[0, 0, -1])
    ws = engine_weight_and_size(fn_sls_wet)
    return DisciplineResult(
        "propulsion",
        "pyCycle single-spool afterburning turbojet deck, MIL-E-5008B inlet recovery, "
        "Raymer eqs. 10.1-10.3 weight scaling",
        {"deck": deck, "deck_key": key, "deck_cached": cached,
         "deck_wall_time_s": raw.get("wall_time_s"),
         "fn_sls_dry_kN": fn_sls_dry / 1000, "fn_sls_reheat_kN": fn_sls_wet / 1000,
         "sls_airflow_kg_s": raw["sls"]["W_lbm_s"] * LBM,
         "tsfc_sls_dry_per_h": float(deck.ff[0, 0, 0] / deck.fn[0, 0, 0] * 9.80665 * 3600),
         "tsfc_sls_reheat_per_h": float(deck.ff[0, 0, -1] / deck.fn[0, 0, -1] * 9.80665 * 3600),
         **{f"engine_{k}": v for k, v in ws.items()}},
        UNCERTAINTIES,
        validity,
    )
