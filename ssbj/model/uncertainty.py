"""Monte Carlo error bars for the end-to-end result (Phase 1 version).

Every discipline declares independent multiplicative error factors
(ssbj.core.interface.Uncertainty). The Monte Carlo samples all of them,
re-runs the fast disciplines (weights, mission) with the polar and engine
deck built once, and reports percentiles. Correlations between factors are
not modelled except where a discipline declares an explicit shared factor
(weights.class_structure). Phase 2 replaces this with proper propagation.

The sample size, seed and every factor sigma are recorded with the result.
"""
from __future__ import annotations

import multiprocessing as mp
import os
from collections import Counter

import numpy as np

from ssbj.core.interface import Factors
from ssbj.disciplines.mission.analysis import MissionInfeasible, analyse
from ssbj.disciplines.weights.raymer_transport import build_weights

PERCENTILES = (2.5, 16.0, 50.0, 84.0, 97.5)


def collect(results: dict) -> list:
    out = []
    for r in results.values():
        out += r.uncertainties
    return out


def sample_factors(uncertainties, n: int, seed: int) -> list[Factors]:
    rng = np.random.default_rng(seed)
    names = sorted({u.name for u in uncertainties})
    sig = {u.name: u.sigma_rel for u in uncertainties}
    draws = rng.standard_normal((n, len(names)))
    out = []
    for row in draws:
        out.append(Factors({k: float(max(1.0 + sig[k] * z, 0.05)) for k, z in zip(names, row)}))
    return out


_CTX = {}


def _init(ctx):
    _CTX.update(ctx)


def _one(f: Factors):
    """One sample. The range and design missions are recorded independently (D-017)."""
    c = _CTX
    w = build_weights(c["aircraft"], c["engine_kg"], c["case"].mission.payload, f)
    row = {"oew_kg": w.outputs["oew_kg"], "engine_dry_mass_kg": c["engine_kg"] * f("prop.weight")}
    try:
        m = analyse(c["case"].mission, c["polar"], c["deck"], c["s_ref"], w.outputs["oew_kg"],
                    c["mtow"], c["fuel_capacity"], f)
    except MissionInfeasible as e:  # OEW + payload > MTOW: neither mission can start
        return row | {"range_reason": str(e), "design_reason": str(e)}
    r, d = m.outputs["range"], m.outputs["design_mission"]
    if "infeasible" in r:
        row["range_reason"] = r["infeasible"]
    else:
        row |= {"range_nmi": r["range_nmi"], "range_ramp_fuel_kg": r["ramp_fuel_kg"],
                "ld_cruise": r["ld_cruise"], "tsfc_cruise_per_h": r["tsfc_cruise_per_h"],
                "transonic_thrust_margin": r["transonic_thrust_margin"]}
    if "infeasible" in d:
        row["design_reason"] = d["infeasible"]
    else:
        row |= {"design_ramp_fuel_kg": d["ramp_fuel_kg"], "design_trip_fuel_kg": d["trip_fuel_kg"],
                "design_block_fuel_kg": d["block_fuel_kg"]}
    return row


def _segment(reason: str) -> str:
    """Group key: the segment name or the message up to its first number."""
    import re

    head = reason.split(":")[0]
    return re.split(r"\s*\(?\d", head)[0].strip()


def monte_carlo(case, results: dict, aircraft, n: int = 200, seed: int = 20261004,
                processes: int | None = None) -> dict:
    uncs = collect(results)
    factors = sample_factors(uncs, n, seed)
    ctx = {"case": case, "aircraft": aircraft, "polar": results["aerodynamics"].outputs["polar"],
           "deck": results["propulsion"].outputs["deck"],
           "engine_kg": results["propulsion"].outputs["engine_dry_weight_kg"],
           "s_ref": aircraft.s_ref, "mtow": case.design.weights.design_gross_mass_kg,
           "fuel_capacity": case.design.weights.fuel_capacity_kg}
    procs = processes or min(4, os.cpu_count() or 1)
    if procs > 1:
        with mp.get_context("fork").Pool(procs, initializer=_init, initargs=(ctx,)) as pool:
            rows = pool.map(_one, factors, chunksize=max(1, n // (4 * procs)))
    else:
        _init(ctx)
        rows = [_one(f) for f in factors]
    stats = {}
    for k in ("oew_kg", "engine_dry_mass_kg", "range_nmi", "range_ramp_fuel_kg", "ld_cruise",
              "tsfc_cruise_per_h", "transonic_thrust_margin", "design_ramp_fuel_kg", "design_trip_fuel_kg",
              "design_block_fuel_kg"):
        v = np.array([r[k] for r in rows if k in r], dtype=float)
        if len(v) < 2:
            continue
        stats[k] = {f"p{p:g}": float(np.percentile(v, p)) for p in PERCENTILES} | {
            "mean": float(v.mean()), "std": float(v.std(ddof=1)), "n": int(len(v))}
    range_bad = [r["range_reason"] for r in rows if "range_reason" in r]
    design_bad = [r["design_reason"] for r in rows if "design_reason" in r]
    return {
        "n_samples": n, "seed": seed,
        "range_mission": {"n_feasible": n - len(range_bad), "n_infeasible": len(range_bad),
                          "by_segment": dict(Counter(map(_segment, range_bad))),
                          "examples": sorted(set(range_bad))[:5]},
        "design_mission": {"n_feasible": n - len(design_bad), "n_infeasible": len(design_bad),
                           "by_segment": dict(Counter(map(_segment, design_bad))),
                           "examples": sorted(set(design_bad))[:5]},
        "factors": [u.__dict__ for u in uncs],
        "stats": stats,
        "note": ("Independent factors (plus declared shared factors); 95 % interval = p2.5-p97.5. "
                 "Each output's percentiles are over the samples in which its own mission was flyable "
                 "(conditional; column n), so they are biased toward low-drag, light samples. The "
                 "infeasible counts are part of the result."),
    }
