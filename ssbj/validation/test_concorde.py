"""Acceptance test for Phase 1: blind Concorde reproduction (honesty rule 5: tests are the gate).

Runs the case exactly as `ssbj run ssbj/validation/concorde/case.yaml` does,
with the Monte Carlo, and requires every published gate value to fall inside
the model's 95 % interval. Uses the committed engine-deck and wave-drag
caches; if those are stale (code changed) they are regenerated, which takes
about 20 minutes.
"""
from pathlib import Path

import pytest

from ssbj.model.run import run_case
from ssbj.runs.db import RunDB

CASE = Path(__file__).parent / "concorde" / "case.yaml"


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    return run_case(CASE, n_samples=200, db=RunDB(tmp_path_factory.mktemp("runs")))


def test_gates_inside_error_bar(result):
    comp = result["comparison"]
    failed = [g["id"] for g in comp["gates"] if not g.get("inside_95")]
    assert not failed, f"published values outside the 95 % interval: {failed}"


def test_result_is_recorded_with_provenance(result, tmp_path_factory):
    assert result["code_version"]["git_sha"]
    assert result["monte_carlo"]["n_samples"] == 200
    assert Path(result["report_path"]).read_text().startswith("# Run report: concorde")


def test_infeasible_fraction_is_reported(result):
    """Infeasible samples are part of the result, not discarded silently. No threshold is gated:
    one chosen after seeing the result would be tuning (see reports/decision_log.md, D-009)."""
    mc = result["monte_carlo"]
    report = Path(result["report_path"]).read_text()
    assert "conditional" in report
    for name in ("range_mission", "design_mission"):
        m = mc[name]
        assert m["n_feasible"] + m["n_infeasible"] == mc["n_samples"]
        if m["n_infeasible"]:
            assert f"{name}: {m['n_infeasible']} of" in report
