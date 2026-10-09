"""Two-spool engine decks (D-024): build, match to sea-level data, sweep the envelope, apply limits.

The deck records, at every (Mach, altitude, T4 fraction), net thrust, fuel flow, compressor-exit
temperature T3 and HP spool speed. At load, each point's maximum dry setting is the highest T4
fraction that respects T4_max, T3_max (core limit) and the HP-speed limit; the dry settings are
re-sampled below that limit. Full reheat is evaluated at T4_max during generation and scaled to the
limited dry thrust when a limit binds (documented approximation).

Inlet recovery follows MIL-E-5008B (as in the single-spool deck); intake design is roadmap item 4.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import multiprocessing as mp
import os
import time
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ssbj.core.atmosphere import FT, LBF, LBM, atmosphere
from ssbj.core.interface import DisciplineResult, Factors, Uncertainty, Validity
from ssbj.disciplines.propulsion.deck import (
    ALT_FT,
    MACH,
    REF_ENGINE,
    T4_FRACS,
    EngineDeck,
    engine_weight_and_size,
    in_envelope,
    ram_recovery,
)

CACHE_DIR = Path(os.environ.get("SSBJ_DECK_CACHE", Path(__file__).parent / "decks"))

UNCERTAINTIES = [
    Uncertainty("prop.thrust", 0.15,
                "Owner decision D-033 (was 5 %): widened because both engine validations fail at 2 x 5 % "
                "(Olympus 593 cruise thrust +23 %, airflow +37-43 %). Generic maps, no duct losses, "
                "installation drags not modelled.", "available thrust"),
    Uncertainty("prop.sfc", 0.15,
                "Owner decision D-033 (was 5 %): widened because the STCA turbofan check gives SFC -17 %. "
                "Generic efficiencies and maps; no offtakes.", "fuel flow at given thrust"),
    Uncertainty("prop.weight", 0.30,
                "Scaled from Raymer's 1990s-technology reference engine; biased low for older engines.",
                "engine dry weight"),
]

LIMITS = [
    "Generic compressor and turbine maps (pyCycle LPC/Fan/HPC/HPT/LPT) scaled to the design point.",
    "Dry: fixed nozzle throat area; reheat: nozzle opened to hold the LP compressor on its dry "
    "operating line. Real schedules differ.",
    "Validation errors exceed the original 5 % sigmas (now 15 %, D-033): Olympus 593 (two-spool turbojet) "
    "cruise thrust +23 % and airflow +43 %; NASA STCA (bought-core turbofan) SFC -17 % and BPR +61 %. "
    "No duct or mixer pressure losses are modelled.",
    "Inlet recovery is the MIL-E-5008B standard schedule, not a designed intake.",
    "Reheat at a limited dry point is scaled from the T4_max reheat/dry ratio.",
    "Spillage, bypass, bleed and boat-tail drag not modelled; no customer power offtake.",
    "Idle and descent fuel flow extrapolated below 65 % of T4_max.",
]


def eta_isentropic(pr: float, eta_poly: float, gamma: float = 1.4) -> float:
    k = (gamma - 1.0) / gamma
    return (pr**k - 1.0) / (pr ** (k / eta_poly) - 1.0)


# ----------------------------------------------------------------------------- problem
def new_problem(spec):
    import openmdao.api as om

    from ssbj.disciplines.propulsion.two_spool_cycle import DesignAndOffDesign

    byp = spec.type == "mixed_flow_turbofan"
    ab = spec.afterburner
    p = om.Problem(reports=False)
    p.model = DesignAndOffDesign(bypass=byp, afterburner=ab)
    p.setup()
    p.model.DESIGN.nonlinear_solver.options["err_on_non_converge"] = True
    p.model.OD.nonlinear_solver.options["err_on_non_converge"] = True
    p.set_solver_print(level=-1)
    p.set_val("DESIGN.fc.alt", spec.design_alt_ft, units="ft")
    p.set_val("DESIGN.fc.MN", max(spec.design_mach, 1e-6))
    p.set_val("DESIGN.inlet.ram_recovery", float(ram_recovery(spec.design_mach)))
    p.set_val("DESIGN.balance.rhs:W", spec.fn_design_kN or spec.fn_sls_dry_kN, units="kN")
    p.set_val("DESIGN.balance.rhs:FAR", spec.t4_max_K, units="degK")
    p.set_val("DESIGN.lpc.PR", spec.lpc_pr)
    p.set_val("DESIGN.hpc.PR", spec.hpc_pr)
    p.set_val("DESIGN.lpc.eff", eta_isentropic(spec.lpc_pr, spec.lpc_eff_poly))
    p.set_val("DESIGN.hpc.eff", eta_isentropic(spec.hpc_pr, spec.hpc_eff_poly))
    p.set_val("DESIGN.hpt.eff", spec.hpt_eff)
    p.set_val("DESIGN.lpt.eff", spec.lpt_eff)
    if byp:
        p.set_val("DESIGN.balance.rhs:BPR", spec.mixer_er)
    for pt in ("DESIGN", "OD"):
        p.set_val(f"{pt}.burner.dPqP", spec.burner_dpqp)
        p.set_val(f"{pt}.nozz.Cv", spec.nozzle_cv)
        if ab:
            p.set_val(f"{pt}.ab.dPqP", spec.ab_dpqp)
        for b, frac in (("cool_hpt", spec.cool_hpt_frac), ("cool_lpt", spec.cool_lpt_frac)):
            p.set_val(f"{pt}.hpc.{b}:frac_W", frac)
            p.set_val(f"{pt}.hpc.{b}:frac_P", 1.0)
            p.set_val(f"{pt}.hpc.{b}:frac_work", 1.0)
        p.set_val(f"{pt}.hpt.cool_hpt:frac_P", 1.0)
        p.set_val(f"{pt}.lpt.cool_lpt:frac_P", 0.0)
    w_guess = spec.fn_sls_dry_kN * 1000 / LBF / (80.0 if not byp else 45.0)
    p["DESIGN.balance.W"] = w_guess
    p["DESIGN.balance.FAR"] = 0.02
    p["DESIGN.balance.hpt_PR"] = 3.0
    p["DESIGN.balance.lpt_PR"] = 2.0
    T, P, *_ = atmosphere(spec.design_alt_ft * FT)
    m = spec.design_mach
    p["DESIGN.fc.balance.Pt"] = P * (1 + 0.2 * m * m) ** 3.5 / 6894.757
    p["DESIGN.fc.balance.Tt"] = T * (1 + 0.2 * m * m) * 1.8
    p.set_val("OD.fc.MN", max(spec.design_mach, 1e-6))
    p.set_val("OD.fc.alt", spec.design_alt_ft, units="ft")
    p.set_val("OD.balance.rhs:FAR", spec.t4_max_K, units="degK")
    p["OD.balance.W"] = w_guess
    p["OD.balance.FAR"] = 0.02
    p["OD.balance.LP_Nmech"] = 4000.0
    p["OD.balance.HP_Nmech"] = 12000.0
    p["OD.hpt.PR"] = 3.0
    p["OD.lpt.PR"] = 2.0
    if byp:
        p["DESIGN.balance.BPR"] = 1.5
        p["OD.balance.BPR"] = 1.5
        p["DESIGN.mixer.balance.P_tot"] = 30.0
        p["OD.mixer.balance.P_tot"] = 30.0
    return p


class _Solver:
    """Off-design point solver with full-state restore (failed solves leave NaNs behind)."""

    def __init__(self, spec):
        self.spec = spec
        self.p = new_problem(spec)
        self.p.run_model()
        self.vec = self.p.model._outputs.asarray()
        self.seed = self.vec.copy()
        self.last = self.seed.copy()
        self.n_hp_design = float(self.p.get_val("DESIGN.HP_Nmech", units="rpm")[0])
        self.mach = max(spec.design_mach, 1e-6)
        self.rline_dry = float(self.p.get_val("DESIGN.lpc.map.RlineMap")[0])
        self.nc_last = None
        self.nc_last = self._nc()

    def _nc(self):
        return np.array([float(self.p.get_val("OD.lpc.map.NcMap")[0]),
                         float(self.p.get_val("OD.hpc.map.NcMap")[0])])

    def solve(self, alt_ft, frac, ab_far=0.0):
        p = self.p
        for guess in (self.last, self.seed):
            self.vec[:] = guess  # auto-IVC inputs live in this vector too: set inputs after restoring
            if guess is self.last:
                self.nc_last = self._nc()
            p.set_val("OD.fc.MN", max(self.mach, 1e-6))
            p.set_val("OD.inlet.ram_recovery", float(ram_recovery(self.mach)))
            p.set_val("OD.fc.alt", alt_ft, units="ft")
            p.set_val("OD.balance.rhs:FAR", self.spec.t4_max_K * frac, units="degK")
            if self.spec.afterburner:
                p.set_val("OD.ab.Fl_I:FAR", ab_far)
            p.set_val("OD.wctl.s", 1.0 if ab_far > 0 else 0.0)
            if ab_far > 0:
                p.set_val("OD.wctl.rline_tgt", self.rline_dry)
            try:
                p.run_model()
            except Exception:
                continue
            if not np.all(np.isfinite(self.vec)):
                continue
            nc = self._nc()
            if self.nc_last is not None and np.max(np.abs(nc - self.nc_last)) > 0.08:
                continue  # jumped to another solution branch: not a continuation of this one
            self.last = self.vec.copy()
            self.nc_last = nc
            return True
        self.vec[:] = self.last
        return False

    def read(self):
        p = self.p
        f = float(p.get_val("OD.perf.Fn", units="N")[0])
        w = float(p.get_val("OD.perf.Wfuel", units="kg/s")[0])
        t3 = float(p.get_val("OD.hpc.Fl_O:tot:T", units="degK")[0])
        n2 = float(p.get_val("OD.HP_Nmech", units="rpm")[0]) / self.n_hp_design
        wa = float(p.get_val("OD.inlet.Fl_O:stat:W", units="kg/s")[0])
        if not (f > 0 and np.isfinite(w)):
            return (np.nan,) * 5
        return f, w, t3, n2, wa

    def within_limits(self) -> bool:
        f, w, t3, n2, wa = self.read()
        if not np.isfinite(f):
            return False
        sp = self.spec
        if sp.t3_max_K is not None and t3 > sp.t3_max_K + 0.5:
            return False
        return not (sp.hp_speed_max_frac is not None and n2 > sp.hp_speed_max_frac + 5e-4)

    def solve_limited(self, alt_ft, f_floor: float = 0.55, step: float = 0.02) -> float | None:
        """Highest T4 fraction (<= 1) that converges and respects the T3 and HP-speed limits.

        Walks T4 in small steps from the previous point's setting (large jumps do not converge),
        then bisects between the last setting inside the limits and the first outside.
        """
        f = min(getattr(self, "f_prev", 1.0), 1.0)

        def ok(x):
            return self.solve(alt_ft, x) and self.within_limits()

        if ok(f):
            good_f, good = f, self.last.copy()
            bad_f = None
            while good_f < 1.0:  # walk up
                x = min(good_f + step, 1.0)
                if ok(x):
                    good_f, good = x, self.last.copy()
                else:
                    bad_f = x
                    self.last = good.copy()
                    break
        else:
            bad_f, good_f, good = f, None, None
            x = f
            while x - step >= f_floor:  # walk down
                x -= step
                if ok(x):
                    good_f, good = x, self.last.copy()
                    break
            if good_f is None:
                return None
        if bad_f is not None:
            lo, hi = good_f, bad_f
            for _ in range(8):
                mid = 0.5 * (lo + hi)
                self.last = good.copy()
                if ok(mid):
                    lo, good = mid, self.last.copy()
                else:
                    hi = mid
                if hi - lo < 1e-3:
                    break
            good_f = lo
        self.last = good
        self.solve(alt_ft, good_f)
        self.f_prev = good_f
        return good_f

    def t_ab(self):
        return float(self.p.get_val("OD.ab.Fl_O:tot:T", units="degK")[0]) - self.spec.t_ab_K

    def reheat(self, alt_ft):
        return self.reheat_at(alt_ft, 1.0)

    def reheat_at(self, alt_ft, frac):
        """Ramp then secant-iterate the afterburner FAR to reach t_ab_K at T4 fraction ``frac``.

        The caller must have just solved the dry point at ``frac``: its LP operating line is held.
        """
        self.rline_dry = float(self.p.get_val("OD.lpc.map.RlineMap")[0])
        x, t = 0.0, self.t_ab()
        x_prev, t_prev = x, t
        while t < 0:
            x_prev, t_prev = x, t
            x = round(x + 0.005, 4)
            if x > 0.06 or not self.solve(alt_ft, frac, x):
                return (np.nan,) * 5
            t = self.t_ab()
        x0, t0, x1, t1 = x_prev, t_prev, x, t
        for _ in range(8):
            if abs(t1) < 2.0 or t1 == t0:
                break
            x0, x1, t0 = x1, float(np.clip(x1 - t1 * (x1 - x0) / (t1 - t0), 1e-4, 0.06)), t1
            if not self.solve(alt_ft, frac, x1):
                return (np.nan,) * 5
            t1 = self.t_ab()
        return self.read() if abs(t1) < 10.0 else (np.nan,) * 5

    def go_to(self, mach, alt_ft, steps=8) -> float | None:
        """Limited continuation from the current state to (mach, alt); returns the final T4 fraction."""
        m0 = self.mach
        h0 = float(self.p.get_val("OD.fc.alt", units="ft")[0])
        f = None
        for t in np.linspace(0.0, 1.0, steps + 1)[1:]:
            self.mach = m0 + (mach - m0) * t
            f = self.solve_limited(h0 + (alt_ft - h0) * t)
        return f

    def at(self, mach, alt_ft) -> bool:
        """True if the current converged state is at (mach, alt)."""
        return (abs(float(self.p.get_val("OD.fc.MN")[0]) - max(mach, 1e-6)) < 1e-6
                and abs(float(self.p.get_val("OD.fc.alt", units="ft")[0]) - alt_ft) < 0.5)


# ----------------------------------------------------------------------------- matching
def match_sls(spec, airflow_kg_s: float, fn_reheat_kN: float | None, tol: float = 1e-3):
    """T4_max so SLS airflow matches; afterburner temperature so SLS reheat thrust matches."""

    def airflow(t4):
        s = _Solver(spec.model_copy(update={"t4_max_K": t4}))
        return float(s.p.get_val("DESIGN.inlet.Fl_O:stat:W", units="kg/s")[0])

    x0, x1 = spec.t4_max_K, spec.t4_max_K - 50.0
    f0, f1 = airflow(x0) - airflow_kg_s, airflow(x1) - airflow_kg_s
    for _ in range(15):
        if abs(f1) < tol * airflow_kg_s or f1 == f0:
            break
        x0, x1, f0 = x1, float(np.clip(x1 - f1 * (x1 - x0) / (f1 - f0), 1000, 2100)), f1
        f1 = airflow(x1) - airflow_kg_s
    spec = spec.model_copy(update={"t4_max_K": round(x1, 1)})
    if fn_reheat_kN is None or not spec.afterburner:
        return spec
    s = _Solver(spec.model_copy(update={"t_ab_K": 1500.0}))
    target = fn_reheat_kN * 1000

    def thrust_at(t_ab):
        s.spec = s.spec.model_copy(update={"t_ab_K": t_ab})
        s.mach = 1e-6
        s.last = s.seed.copy()
        s.solve(0.0, 1.0)
        return s.reheat(0.0)[0]

    a, b = 1100.0, 2200.0
    fa = thrust_at(a) - target
    for _ in range(25):
        m = 0.5 * (a + b)
        fm = thrust_at(m) - target
        if abs(fm) < tol * target:
            break
        if (fm < 0) == (fa < 0):
            a, fa = m, fm
        else:
            b = m
    return spec.model_copy(update={"t_ab_K": round(m, 1)})


def match_reheat_sls(spec, fn_reheat_kN: float, tol: float = 1e-3):
    """Afterburner exit temperature so SLS full reheat (at the limited dry setting) gives fn_reheat_kN."""
    s = _Solver(spec)
    if s.go_to(0.0, 0.0, steps=40) is None or not s.at(0.0, 0.0):
        raise RuntimeError("engine did not converge at SLS")
    top, frac = s.last.copy(), s.f_prev
    target = fn_reheat_kN * 1000

    def thrust(t_ab):
        s.spec = s.spec.model_copy(update={"t_ab_K": t_ab})
        s.last = top.copy()
        s.solve(0.0, frac)
        return s.reheat_at(0.0, frac)[0] - target

    a, b = 1100.0, 2200.0
    fa = thrust(a)
    for _ in range(25):
        m = 0.5 * (a + b)
        fm = thrust(m)
        if abs(fm) < tol * target:
            break
        if (fm < 0) == (fa < 0):
            a, fa = m, fm
        else:
            b = m
    return spec.model_copy(update={"t_ab_K": round(m, 1)})


def size_to_sls(spec, tol: float = 1e-3, max_iter: int = 6):
    """Set fn_design_kN so the limited max-dry SLS thrust equals fn_sls_dry_kN.

    The cycle scales with design airflow, so thrust at any point scales with fn_design: a few
    proportional updates converge. Returns (sized spec, SLS diagnostics).
    """
    fn_d = spec.fn_design_kN or spec.fn_sls_dry_kN
    for _ in range(max_iter):
        sp = spec.model_copy(update={"fn_design_kN": fn_d})
        s = _Solver(sp)
        frac = s.go_to(0.0, 0.0, steps=40)
        if frac is None or not s.at(0.0, 0.0):
            raise RuntimeError("engine did not converge at SLS during sizing")
        f, w, t3, n2, wa = s.read()
        ratio = spec.fn_sls_dry_kN * 1000 / f
        if abs(ratio - 1) < tol:
            break
        fn_d *= ratio
    return sp, {"fn_sls_N": f, "w_sls_kg_s": wa, "t4_frac_sls": frac, "n2_frac_sls": n2, "t3_sls_K": t3}


# ----------------------------------------------------------------------------- deck
def _row(args):
    spec, mach = args
    warnings.filterwarnings("ignore")
    s = _Solver(spec)
    n_alt, n_t4 = len(ALT_FT), len(T4_FRACS)
    out = np.full((n_alt, n_t4 + 1, 6), np.nan)  # fn, ff, t3, n2, w, T4 fraction
    h_start = float(np.interp(mach, [0.0, 0.9, 1.4, 2.0, 2.4], [0.0, 25000.0, 40000.0, 50000.0, 55000.0]))
    s.go_to(mach, h_start, steps=12)
    i0 = int(np.argmin(np.abs(ALT_FT - h_start)))
    start = None
    for order in (range(i0, n_alt), range(i0 - 1, -1, -1)):
        if start is not None:
            s.last = start.copy()
        for i in order:
            h = ALT_FT[i]
            if not in_envelope(mach, h):
                continue
            f_max = s.solve_limited(h)
            if f_max is None:
                continue
            top = s.last.copy()
            if i == i0:
                start = top.copy()
            for j, frac in enumerate(f_max - (1.0 - T4_FRACS)):  # settings below the limited maximum
                if s.solve(h, frac):
                    out[i, j, :5] = s.read()
                    out[i, j, 5] = frac
            s.last = top
            if spec.afterburner and spec.t_ab_K and s.solve(h, f_max):
                out[i, n_t4, :5] = s.reheat_at(h, f_max)
                out[i, n_t4, 5] = f_max
            s.last = top
    return mach, out


def source_hash() -> str:
    parts = [(Path(__file__).parent / "two_spool_cycle.py").read_text()]
    parts += [inspect.getsource(f) for f in (new_problem, _Solver, _row, ram_recovery, in_envelope)]
    parts.append(repr((MACH.tolist(), ALT_FT.tolist(), T4_FRACS.tolist())))
    return hashlib.sha256("".join(parts).encode()).hexdigest()[:12]


def deck_key(spec) -> str:
    blob = json.dumps({"engine": spec.model_dump(), "src": source_hash()}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def load_or_generate(spec, processes: int | None = None) -> tuple[dict, str, bool]:
    key = deck_key(spec)
    path = CACHE_DIR / f"deck2s_{key}.json"
    if path.exists():
        return json.loads(path.read_text()), key, True
    t0 = time.perf_counter()
    procs = processes or min(4, os.cpu_count() or 1)
    jobs = [(spec, float(m)) for m in MACH]
    if procs > 1:
        with mp.get_context("spawn").Pool(procs) as pool:
            rows = pool.map(_row, jobs)
    else:
        rows = [_row(j) for j in jobs]
    rows.sort(key=lambda r: r[0])
    arr = np.stack([r[1] for r in rows])  # (mach, alt, setting, [fn, ff, t3, n2, w])
    raw = {"key": key, "engine": spec.model_dump(), "wall_time_s": time.perf_counter() - t0,
           "grid": {"mach": MACH.tolist(), "alt_ft": ALT_FT.tolist(), "t4_fracs": T4_FRACS.tolist()},
           "fn_N": arr[..., 0].tolist(), "ff_kg_s": arr[..., 1].tolist(), "t3_K": arr[..., 2].tolist(),
           "n2_frac": arr[..., 3].tolist(), "w_kg_s": arr[..., 4].tolist(), "t4_frac": arr[..., 5].tolist()}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw))
    return raw, key, False


@dataclass
class LimitedDeck(EngineDeck):
    """EngineDeck generated below the T4 / T3 / HP-speed limited maximum at every point."""

    t4_frac_max: np.ndarray | None = None  # (mach, alt) limited maximum T4 fraction (1.0 = T4 limit)

    @classmethod
    def from_raw2(cls, raw: dict, spec):
        base = EngineDeck.from_raw({"fn_N": raw["fn_N"], "ff_kg_s": raw["ff_kg_s"]}, spec.count)
        fmax = np.array(raw["t4_frac"], dtype=float)[:, :, 0]
        return cls(base.fn, base.ff, base.count, base.filled, base.outside, fmax)


def build_two_spool(spec, processes: int | None = None) -> DisciplineResult:
    raw, key, cached = load_or_generate(spec, processes)
    deck = LimitedDeck.from_raw2(raw, spec)
    validity = Validity("propulsion", list(LIMITS))
    n_fill = int(deck.filled.sum())
    if n_fill:
        validity.warn(f"{n_fill} in-envelope deck points did not converge and were filled from neighbours")
    lim = deck.t4_frac_max
    if lim is not None and np.nanmin(lim) < 0.999:
        validity.warn(f"T3 or HP-speed limit binds at {(lim < 0.999).sum()} (Mach, altitude) points "
                      f"(T4 down to {np.nanmin(lim):.2f} of T4_max)")
    fn_dry, fn_wet = float(deck.fn[0, 0, 0]), float(deck.fn[0, 0, -1])
    ws = engine_weight_and_size(fn_wet if np.isfinite(fn_wet) and spec.afterburner else fn_dry)
    w0 = float(np.array(raw["w_kg_s"])[0, 0, 0])
    return DisciplineResult(
        "propulsion",
        f"pyCycle two-spool {spec.type.replace('_', ' ')} deck with T4/T3/HP-speed limits, "
        "MIL-E-5008B inlet, Raymer eqs. 10.1-10.3 weight scaling",
        {"deck": deck, "deck_key": key, "deck_cached": cached, "deck_wall_time_s": raw.get("wall_time_s"),
         "fn_sls_dry_kN": fn_dry / 1000, "fn_sls_reheat_kN": fn_wet / 1000, "sls_airflow_kg_s": w0,
         "tsfc_sls_dry_per_h": float(deck.ff[0, 0, 0] / deck.fn[0, 0, 0] * 9.80665 * 3600),
         **{f"engine_{k}": v for k, v in ws.items()}},
        UNCERTAINTIES, validity)


# ----------------------------------------------------------------------------- validation
def olympus_validation_point() -> dict:
    """Concorde's two-spool engine at the published cruise points (max dry, T4_max).

    The engine is the one defined in ssbj/validation/concorde/case.yaml (sea-level data only).
    """
    from ssbj.specs.schema import load_case

    case = load_case(Path(__file__).parents[2] / "validation" / "concorde" / "case.yaml")
    spec = case.design.engine
    if spec.type != "two_spool_turbojet":
        raise ValueError("Concorde case engine is not the two-spool turbojet")
    warnings.filterwarnings("ignore")
    s = _Solver(spec)
    out = {}
    frac = s.go_to(2.0, 53000.0, steps=40) if spec.design_mach == 0 else s.solve_limited(53000.0)
    if spec.design_mach != 0:  # already at the design point; make sure we are at M2.0 / 53 kft
        s.mach = 2.0
        frac = s.go_to(2.0, 53000.0, steps=4)
    if frac is None or not s.at(2.0, 53000.0):
        raise RuntimeError("engine did not converge at M2.0 / 53,000 ft: validation not evaluated")
    f, w, t3, n2, wa = s.read()
    out |= {"fn_N_M2_53k": f, "tsfc_per_h_M2_53k": w * 9.80665 / f * 3600, "t3_K_M2_53k": t3,
            "n2_frac_M2_53k": n2, "w_kg_s_M2_53k": wa, "t4_frac_M2_53k": frac}
    frac = s.go_to(2.0, 55000.0, steps=3)
    if frac is None or not s.at(2.0, 55000.0):
        raise RuntimeError("engine did not converge at M2.0 / 55,000 ft: validation not evaluated")
    out["w_kg_s_M2_55k"] = s.read()[4]
    out["fn_N_M2_55k"] = s.read()[0]
    return out


def stca_validation_point() -> dict:
    """Design point of the NASA 55t STCA turbofan (ssbj/validation/stca_engine/engine.yaml)."""
    import yaml

    from ssbj.specs.schema import TwoSpoolEngine

    raw = yaml.safe_load((Path(__file__).parents[2] / "validation" / "stca_engine" / "engine.yaml").read_text())
    spec = TwoSpoolEngine.model_validate(raw["engine"])
    warnings.filterwarnings("ignore")
    p = new_problem(spec)
    p.model.OD.nonlinear_solver.options["err_on_non_converge"] = False  # only the design point is checked
    p.run_model()
    d = "DESIGN."
    return {"fn_lbf": float(p.get_val(d + "perf.Fn", units="lbf")[0]),
            "tsfc_per_h": float(p.get_val(d + "perf.TSFC", units="lbm/(h*lbf)")[0]),
            "bpr": float(p.get_val(d + "splitter.BPR")[0]),
            "t3_R": float(p.get_val(d + "hpc.Fl_O:tot:T", units="degR")[0]),
            "npr": float(p.get_val(d + "nozz.PR")[0]),
            "wc2_lbm_s": float(p.get_val(d + "lpc.Wc", units="lbm/s")[0]),
            "w_lbm_s": float(p.get_val(d + "inlet.Fl_O:stat:W", units="lbm/s")[0])}


_ = (atmosphere, FT, LBM, REF_ENGINE, Factors)  # re-exported names used by callers
