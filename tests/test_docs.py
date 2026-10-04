from pathlib import Path

from ssbj.docs.register import render


def test_known_limits_register_in_sync():
    path = Path(__file__).resolve().parents[1] / "ssbj" / "docs" / "known_limits.md"
    assert path.read_text() == render(), "run `python -m ssbj limits` and commit the result"


def test_json_schema_in_sync():
    import json

    from ssbj.specs.schema import json_schema

    path = Path(__file__).resolve().parents[1] / "ssbj" / "specs" / "case.schema.json"
    assert json.loads(path.read_text()) == json_schema(), "run `python -m ssbj schema`"
