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
    c = _CTX
    try:
        w = build_weights(c["aircraft"], c["engine_kg"], c["case"].mission.payload, f)
        m = analyse(c["case"].mission, c["polar"], c["deck"], c["s_ref"], w.outputs["oew_kg"],
                    c["mtow"], c["fuel_capacity"], f)
    except MissionInfeasible as e:
        return {"ok": False, "reason": str(e)}
    r, d = m.outputs["range"], m.outputs["design_mission"]
    return {"ok": True, "oew_kg": w.outputs["oew_kg"], "range_nmi": r["range_nmi"],
            "range_ramp_fuel_kg": r["ramp_fuel_kg"], "design_ramp_fuel_kg": d["ramp_fuel_kg"],
            "design_trip_fuel_kg": d["trip_fuel_kg"], "design_block_fuel_kg": d["block_fuel_kg"],
            "transonic_thrust_margin": min(r["transonic_thrust_margin"], d["transonic_thrust_margin"])}


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
    ok = [r for r in rows if r["ok"]]
    stats = {}
    for k in ("oew_kg", "range_nmi", "range_ramp_fuel_kg", "design_ramp_fuel_kg", "design_trip_fuel_kg",
              "design_block_fuel_kg", "transonic_thrust_margin"):
        v = np.array([r[k] for r in ok], dtype=float)
        stats[k] = {f"p{p:g}": float(np.percentile(v, p)) for p in PERCENTILES} | {
            "mean": float(v.mean()), "std": float(v.std(ddof=1))}
    return {
        "n_samples": n, "n_ok": len(ok), "n_infeasible": n - len(ok), "seed": seed,
        "infeasible_reasons": sorted({r["reason"] for r in rows if not r["ok"]})[:10],
        "infeasible_by_segment": dict(Counter(r["reason"].split(":")[0] for r in rows if not r["ok"])),
        "factors": [u.__dict__ for u in uncs],
        "stats": stats,
        "note": ("Independent factors (plus declared shared factors); 95 % interval = p2.5-p97.5. "
                 "Percentiles are over the feasible samples only, i.e. conditional on the modelled "
                 "aircraft being able to fly the profile; the infeasible fraction is part of the result."),
    }
