"""Match unknown cycle temperatures to published sea-level-static engine design data.

When an engine is defined by its published SLS dry thrust, airflow and reheat
thrust (but not its temperatures), T4 is solved so the design point swallows
the published airflow at the published dry thrust, and the afterburner exit
temperature is solved so SLS full reheat gives the published reheat thrust.

This uses design-definition data only (what the engine is), never performance
data the case is validated against (cruise SFC, range, fuel burn). The
decision is logged in reports/decision_log.md.
"""
from __future__ import annotations

import warnings

import numpy as np


def _sls(engine):
    from ssbj.disciplines.propulsion.deck import _new_problem

    warnings.filterwarnings("ignore")
    p = _new_problem(engine)
    p.run_model()
    return p


def match_sls(engine, airflow_kg_s: float, fn_reheat_kN: float, tol: float = 1e-3) -> dict:
    """Return the engine with ``t4_max_K`` and ``t_ab_K`` matched, plus the achieved values."""

    def airflow(t4):
        p = _sls(engine.model_copy(update={"t4_max_K": t4}))
        return float(p.get_val("DESIGN.inlet.Fl_O:stat:W", units="kg/s")[0])

    # secant on T4: specific thrust rises with T4, so airflow at fixed thrust falls
    x0, x1 = engine.t4_max_K, engine.t4_max_K - 50.0
    f0, f1 = airflow(x0) - airflow_kg_s, airflow(x1) - airflow_kg_s
    for _ in range(12):
        if abs(f1) < tol * airflow_kg_s or f1 == f0:
            break
        x0, x1, f0 = x1, float(np.clip(x1 - f1 * (x1 - x0) / (f1 - f0), 1000, 2100)), f1
        f1 = airflow(x1) - airflow_kg_s
    t4 = x1
    eng = engine.model_copy(update={"t4_max_K": t4})

    # afterburner FAR at SLS (OD point at the design condition) for the reheat thrust
    p = _sls(eng)
    p.set_val("OD.balance.rhs:FAR", t4, units="degK")
    target = fn_reheat_kN

    def thrust(far):
        p.set_val("OD.ab.Fl_I:FAR", far)
        p.run_model()
        return float(p.get_val("OD.perf.Fn", units="kN")[0]), float(p.get_val("OD.ab.Fl_O:tot:T", units="degK")[0])

    fars = np.arange(0.0, 0.0601, 0.0025)
    prev = (0.0, thrust(0.0))
    for far in fars[1:]:
        cur = (far, thrust(far))
        if cur[1][0] >= target:
            break
        prev = cur
    else:
        raise ValueError("reheat thrust target not reachable below FAR 0.06")
    (a, (fa, _)), (b, (fb, _)) = prev, cur
    for _ in range(20):
        m = a + (target - fa) * (b - a) / (fb - fa)
        fm, tm = thrust(m)
        if abs(fm - target) < tol * target:
            break
        if fm < target:
            a, fa = m, fm
        else:
            b, fb = m, fm
    eng = eng.model_copy(update={"t_ab_K": round(tm, 1)})
    return {"engine": eng, "t4_max_K": t4, "t_ab_K": tm, "airflow_kg_s": airflow_kg_s + f1,
            "fn_reheat_kN": fm, "ab_far": m}
