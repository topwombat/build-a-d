"""Run database: SQLite index plus one directory of files per run.

Every case stores inputs, code version, outputs, error estimate and wall time.
Default location is ``ssbj/runs/store`` (git-ignored); override with SSBJ_RUNS_DIR.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id       TEXT PRIMARY KEY,
    case_name    TEXT NOT NULL,
    kind         TEXT NOT NULL,
    started_at   TEXT NOT NULL,
    wall_time_s  REAL,
    status       TEXT NOT NULL,
    input_hash   TEXT NOT NULL,
    inputs       TEXT NOT NULL,
    code_version TEXT NOT NULL,
    outputs      TEXT,
    errors       TEXT,
    warnings     TEXT,
    files_dir    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS runs_case ON runs(case_name);
"""


def default_dir() -> Path:
    return Path(os.environ.get("SSBJ_RUNS_DIR", Path(__file__).parent / "store"))


class RunDB:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else default_dir()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "runs.sqlite"
        with self._conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def record(self, case_name: str, kind: str, inputs: dict, input_hash: str, code_version: dict):
        """Context manager that times a run and stores it whether it succeeds or fails."""
        run_id = time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
        files = self.root / run_id
        files.mkdir(parents=True)
        (files / "inputs.json").write_text(json.dumps(inputs, indent=2, default=str))
        run = {"run_id": run_id, "files_dir": files, "outputs": None, "errors": None, "warnings": []}
        t0 = time.perf_counter()
        status = "ok"
        try:
            yield run
        except Exception as e:
            status = "failed"
            run["errors"] = {"type": type(e).__name__, "message": str(e)}
            raise
        finally:
            wall = time.perf_counter() - t0
            if run["outputs"] is not None:
                (files / "outputs.json").write_text(json.dumps(run["outputs"], indent=2, default=str))
            with self._conn() as c:
                c.execute(
                    "INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (run_id, case_name, kind, time.strftime("%Y-%m-%dT%H:%M:%S%z"), wall, status,
                     input_hash, json.dumps(inputs, default=str), json.dumps(code_version),
                     json.dumps(run["outputs"], default=str), json.dumps(run["errors"]),
                     json.dumps(run["warnings"]), str(files)),
                )

    def list(self, case_name: str | None = None) -> list[dict]:
        q = "SELECT run_id, case_name, kind, started_at, wall_time_s, status, input_hash FROM runs"
        args: tuple = ()
        if case_name:
            q += " WHERE case_name = ?"
            args = (case_name,)
        with self._conn() as c:
            return [dict(r) for r in c.execute(q + " ORDER BY started_at", args)]

    def get(self, run_id: str) -> dict:
        with self._conn() as c:
            r = c.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if r is None:
            raise KeyError(run_id)
        d = dict(r)
        for k in ("inputs", "code_version", "outputs", "errors", "warnings"):
            d[k] = json.loads(d[k]) if d[k] else None
        return d
