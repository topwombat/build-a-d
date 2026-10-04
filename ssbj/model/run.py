"""Run a case end to end: nominal OpenMDAO run, Monte Carlo error bars, validation, record, report."""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import yaml

from ssbj.core.provenance import code_version, fingerprint
from ssbj.model.assembly import make_problem
from ssbj.model.uncertainty import monte_carlo
from ssbj.runs.db import RunDB
from ssbj.specs.schema import load_case


def _nominal(p, results) -> dict:
    g = lambda n, u=None: float(p.get_val(n, units=u)[0]) if u else float(p.get_val(n)[0])
    mis = results["mission"].outputs
    rng = mis["range"]
    cruise = next((l for l in rng.get("legs", []) if l["kind"] == "cruise"), None)
    nan = float("nan")
    return {
        "s_ref_m2": g("s_ref", "m**2"),
        "oew_kg": g("oew", "kg"),
        "engine_dry_mass_kg": g("engine_dry_mass", "kg"),
        "fn_sls_reheat_kN": g("fn_sls_reheat", "kN"),
        "cd0_cruise": g("cd0_cruise"),
        "ld_max_cruise": g("ld_max_cruise"),
        "ld_cruise": rng.get("ld_cruise", nan),
        "tsfc_cruise_per_h": rng.get("tsfc_cruise_per_h", nan),
        "cruise_altitude_ft": ([cruise["detail"]["altitude_start_ft"], cruise["detail"]["altitude_end_ft"]]
                               if cruise else None),
        "range_nmi": g("range", "nmi"),
        "range_ramp_fuel_kg": rng.get("ramp_fuel_kg", nan),
        "design_ramp_fuel_kg": g("design_ramp_fuel", "kg"),
        "design_trip_fuel_kg": g("design_trip_fuel", "kg"),
        "design_block_fuel_kg": g("design_block_fuel", "kg"),
        "transonic_thrust_margin": g("transonic_thrust_margin"),
        **_pre_cruise(mis["range"]),
    }


def _pre_cruise(dm: dict) -> dict:
    """Share of trip fuel and distance used before the range cruise starts (max-fuel range mission)."""
    legs = dm.get("legs")
    if not legs:
        return {"pre_cruise_fuel_fraction": float("nan"), "pre_cruise_distance_fraction": float("nan")}
    i = next(k for k, l in enumerate(legs) if l["kind"] == "cruise")
    trip = [l for l in legs if l["kind"] != "taxi"]
    pre = [l for l in legs[:i] if l["kind"] != "taxi"]
    return {"pre_cruise_fuel_fraction": sum(l["fuel_kg"] for l in pre) / sum(l["fuel_kg"] for l in trip),
            "pre_cruise_distance_fraction": sum(l["distance_nmi"] for l in pre)
            / sum(l["distance_nmi"] for l in trip)}


def compare(reference: dict, nominal: dict, mc: dict | None) -> dict:
    out = {"gates": [], "diagnostics": [], "passed": None}
    stats = (mc or {}).get("stats", {})
    for kind in ("gates", "diagnostics"):
        for r in reference.get(kind, []):
            key = r["model_output"]
            row = {k: r.get(k) for k in ("id", "quantity", "value", "range", "unit", "source", "source_quality")}
            row["model_nominal"] = nominal.get(key)
            if key in stats:
                s = stats[key]
                row["model_p2.5"], row["model_p97.5"] = s["p2.5"], s["p97.5"]
                ref_vals = [r["value"]] if r.get("value") is not None else list(r.get("range") or [])
                if ref_vals:
                    row["inside_95"] = all(s["p2.5"] <= v <= s["p97.5"] for v in ref_vals)
            if row.get("model_nominal") is not None and r.get("value"):
                row["nominal_error_pct"] = 100.0 * (row["model_nominal"] - r["value"]) / r["value"]
            out[kind].append(row)
    gates = [g.get("inside_95") for g in out["gates"]]
    out["passed"] = bool(gates) and all(gates) if None not in gates else None
    return out


def run_case(path: str | Path, n_samples: int = 200, seed: int = 20261004, db: RunDB | None = None,
             processes: int | None = None) -> dict:
    path = Path(path)
    case = load_case(path)
    db = db or RunDB()
    inputs = {"case_file": str(path), "case": case.model_dump(), "n_samples": n_samples, "seed": seed}
    ver = code_version()
    with db.record(case.name, "end_to_end", inputs, fingerprint(inputs), ver) as run:
        t0 = time.perf_counter()
        results: dict = {}
        p = make_problem(case, results=results)
        p.run_model()
        nominal = _nominal(p, results)
        aircraft = p.model.geometry._discrete_outputs["aircraft"]
        t_nom = time.perf_counter() - t0
        mc = monte_carlo(case, results, aircraft, n=n_samples, seed=seed, processes=processes) if n_samples else None
        ref_path = path.parent / "reference.yaml"
        comparison = compare(yaml.safe_load(ref_path.read_text()), nominal, mc) if ref_path.exists() else None
        out = {
            "case": case.name,
            "validation_case": case.validation_case,
            "nominal": nominal,
            "monte_carlo": mc,
            "comparison": comparison,
            "disciplines": {k: v.summary() for k, v in results.items()},
            "details": {
                "aero_wave_crosscheck": results["aerodynamics"].outputs["wave_crosscheck"],
                "wetted_areas_m2": results["aerodynamics"].outputs["wetted_areas_m2"],
                "weights_components_kg": results["weights"].outputs["components_kg"],
                "weights_inputs": results["weights"].outputs["inputs"],
                "engine": {k: v for k, v in results["propulsion"].outputs.items() if k != "deck"},
                "mission_range": results["mission"].outputs["range"],
                "mission_design": results["mission"].outputs["design_mission"],
                "geometry_warnings": aircraft.checks,
            },
            "timing_s": {"nominal": t_nom, "total": time.perf_counter() - t0},
            "code_version": ver,
            "run_id": run["run_id"],
        }
        run["outputs"] = json.loads(json.dumps(out, default=_jsonable))
        run["warnings"] = [w for r in results.values() for w in r.validity.warnings]
        report = write_report(out)
        (Path(run["files_dir"]) / "report.md").write_text(report)
        out["report_path"] = str(Path(run["files_dir"]) / "report.md")
    return out


def _jsonable(o):
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def _fmt(v, nd=0):
    if v is None:
        return "-"
    if isinstance(v, (list, tuple)):
        return "-".join(_fmt(x, nd) for x in v)
    return f"{v:,.{nd}f}"


def write_report(out: dict) -> str:
    n = out["nominal"]
    mc = out.get("monte_carlo") or {}
    st = mc.get("stats", {})
    L = [f"# Run report: {out['case']}", ""]
    L += [f"Run `{out['run_id']}`, code `{out['code_version']['git_sha'][:10]}`"
          f"{' (uncommitted changes)' if out['code_version']['dirty'] else ''}.", ""]
    L += ["**The validation set is three or four cases, not twenty.** Treat agreement on one case as "
          "a consistency check, not proof of accuracy.", ""]
    comp = out.get("comparison")
    if comp:
        verdict = {True: "PASS", False: "FAIL", None: "NOT EVALUATED"}[comp["passed"]]
        L += [f"## Validation gates: {verdict}", "",
              "| Quantity | Published | Model nominal | Model 95 % interval | Inside? | Source quality |",
              "|---|---|---|---|---|---|"]
        for g in comp["gates"]:
            L.append(f"| {g['quantity']} | {_fmt(g['value'])} {g['unit']} | {_fmt(g['model_nominal'])} | "
                     f"{_fmt(g.get('model_p2.5'))} to {_fmt(g.get('model_p97.5'))} | "
                     f"{'yes' if g.get('inside_95') else 'no'} | {g['source_quality']} |")
        L += ["", "**What this verdict shows and does not show.** Both gates are one published data point read "
              "two ways. The intervals are wide and conditional on feasibility (see below), so a pass is a "
              "consistency check and a narrow miss is not decisive either. Compare the diagnostics: offsetting errors (e.g. L/D low, TSFC low, "
              "engine weight low) can produce a correct range for the wrong reasons.", ""]
        L += ["", "### Diagnostics (not gates)", "",
              "| Quantity | Published | Model nominal | Model 95 % interval | Source quality |", "|---|---|---|---|---|"]
        for g in comp["diagnostics"]:
            ref = _fmt(g["value"], 3) if g.get("value") else _fmt(g.get("range"), 2)
            L.append(f"| {g['id']} | {ref} {g['unit']} | {_fmt(g['model_nominal'], 3)} | "
                     f"{_fmt(g.get('model_p2.5'), 3)} to {_fmt(g.get('model_p97.5'), 3)} | {g['source_quality']} |")
        L.append("")
    L += ["## Nominal results", ""]
    for k, v in n.items():
        L.append(f"- {k}: {_fmt(v, 4) if isinstance(v, float) and abs(v) < 20 else _fmt(v, 1)}")
    if st:
        L += ["", f"## Error bars (Monte Carlo, {mc['n_samples']} samples, seed {mc['seed']})", "",
              "| Output | n | p2.5 | p16 | p50 | p84 | p97.5 |", "|---|---|---|---|---|---|---|"]
        for k, s_ in st.items():
            nd = 3 if ("margin" in k or "tsfc" in k or "ld_" in k) else 0
            L.append(f"| {k} | {s_['n']} | " + " | ".join(_fmt(s_[f'p{p}'], nd)
                                                        for p in ("2.5", "16", "50", "84", "97.5")) + " |")
        L += ["", mc["note"]]
        for name in ("range_mission", "design_mission"):
            m = mc[name]
            if m["n_infeasible"]:
                L += ["", f"**{name}: {m['n_infeasible']} of {mc['n_samples']} samples could not fly the "
                      "profile**, by segment: " + ", ".join(f"{k} {v}" for k, v in sorted(m["by_segment"].items()))
                      + ". Example: " + m["examples"][0]]
        L += ["", "Error factors sampled (1-sigma, relative):", ""]
        for f in mc["factors"]:
            L.append(f"- `{f['name']}` {f['sigma_rel']:.0%}: {f['basis']}")
    L += ["", "## Warnings raised in this run", ""]
    for d, s in out["disciplines"].items():
        for w in s["warnings"]:
            L.append(f"- {d}: {w}")
    L += ["", "## Where these methods should not be trusted", ""]
    for d, s in out["disciplines"].items():
        for w in s["not_trusted_when"]:
            L.append(f"- {d}: {w}")
    return "\n".join(L) + "\n"
