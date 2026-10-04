"""Command line: ``ssbj run <case.yaml>`` runs a case end to end from a single file."""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ssbj", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run a case file end to end")
    r.add_argument("case", type=Path)
    r.add_argument("--samples", type=int, default=200, help="Monte Carlo samples (0 = nominal only)")
    r.add_argument("--seed", type=int, default=20261004)
    r.add_argument("--processes", type=int, default=None)
    r.add_argument("--runs-dir", type=Path, default=None)
    s = sub.add_parser("schema", help="write the case JSON schema")
    s.add_argument("--out", type=Path, default=Path(__file__).parent / "specs" / "case.schema.json")
    v = sub.add_parser("validate", help="validate a case file without running it")
    v.add_argument("case", type=Path)
    lim = sub.add_parser("limits", help="write the known-limits register from the modules")
    lim.add_argument("--out", type=Path, default=Path(__file__).parent / "docs" / "known_limits.md")
    ls = sub.add_parser("runs", help="list recorded runs")
    ls.add_argument("--case", default=None)
    ls.add_argument("--runs-dir", type=Path, default=None)
    a = ap.parse_args(argv)

    warnings.filterwarnings("ignore")
    if a.cmd == "schema":
        from ssbj.specs.schema import json_schema

        a.out.write_text(json.dumps(json_schema(), indent=2) + "\n")
        print(f"wrote {a.out}")
    elif a.cmd == "validate":
        from ssbj.geometry.parametric import GeometryError, build
        from ssbj.specs.schema import load_case

        c = load_case(a.case)
        try:
            ac = build(c.design)
        except GeometryError as e:
            print("geometry failures:\n  " + "\n  ".join(e.failures))
            return 2
        print(f"{c.name}: valid; geometry warnings: {ac.checks or 'none'}")
    elif a.cmd == "limits":
        from ssbj.docs.register import render

        a.out.write_text(render())
        print(f"wrote {a.out}")
    elif a.cmd == "runs":
        from ssbj.runs.db import RunDB

        for row in RunDB(a.runs_dir).list(a.case):
            print(f"{row['run_id']}  {row['case_name']:<12} {row['status']:<7} {row['wall_time_s']:8.1f} s")
    elif a.cmd == "run":
        from ssbj.model.run import run_case
        from ssbj.runs.db import RunDB

        out = run_case(a.case, a.samples, a.seed, RunDB(a.runs_dir), a.processes)
        print(Path(out["report_path"]).read_text())
        print(f"run {out['run_id']} recorded; report at {out['report_path']}")
        comp = out.get("comparison")
        if comp and comp["passed"] is False:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
