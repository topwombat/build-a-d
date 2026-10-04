"""Code-version and input fingerprints recorded with every result."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path

import ssbj

REPO_ROOT = Path(__file__).resolve().parents[2]


def code_version() -> dict:
    def git(*args):
        try:
            return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True,
                                  timeout=10).stdout.strip()
        except Exception:
            return ""

    sha = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=no", "--", "ssbj"))
    return {
        "package": ssbj.__version__,
        "git_sha": sha or "unknown",
        "dirty": dirty,
        "python": platform.python_version(),
        "libs": _lib_versions(),
    }


def _lib_versions() -> dict:
    out = {}
    for name in ("numpy", "scipy", "openmdao", "pycycle", "pydantic"):
        try:
            mod = __import__(name)
            out[name] = getattr(mod, "__version__", "?")
        except Exception:
            out[name] = None
    try:
        import openvsp

        out["openvsp"] = openvsp.GetVSPVersion()
    except Exception:
        out["openvsp"] = None
    return out


def fingerprint(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]
