import pytest

from ssbj.core.interface import Factors
from ssbj.disciplines.weights.raymer_transport import build_weights
from ssbj.runs.db import RunDB


def test_weights_positive_and_factor_response(concorde_case, concorde_aircraft):
    nom = build_weights(concorde_aircraft, 3000.0, concorde_case.mission.payload)
    assert all(v > 0 for k, v in nom.outputs["components_kg"].items() if k != "apu")
    up = build_weights(concorde_aircraft, 3000.0, concorde_case.mission.payload,
                       Factors({"weights.class_structure": 1.1}))
    d = up.outputs["empty_kg"] - nom.outputs["empty_kg"]
    struct = sum(nom.outputs["components_kg"][k] for k in ("wing", "vertical_tail", "fuselage", "main_gear",
                                                            "nose_gear", "nacelle_group"))
    assert d == pytest.approx(0.1 * struct, rel=1e-9)


def test_wing_equation_hand_check(concorde_aircraft, concorde_case):
    """Raymer eq. 15.25 re-evaluated independently from the recorded inputs."""
    import numpy as np

    r = build_weights(concorde_aircraft, 3000.0, concorde_case.mission.payload).outputs
    i = r["inputs"]
    wdg = concorde_case.design.weights.design_gross_mass_kg / 0.45359237
    scsw = concorde_case.design.weights.control_surface_area_m2 / 0.3048**2
    w = (0.0051 * (wdg * i["Nz"]) ** 0.557 * i["Sw_ft2"] ** 0.649 * i["A"] ** 0.5 * i["tc_root"] ** -0.4
         * (1 + i["taper"]) ** 0.1 / np.cos(np.radians(i["sweep_qc_deg"])) * scsw**0.1)
    assert r["components_nominal_kg"]["wing"] == pytest.approx(w * 0.45359237)


def test_run_db_records_success_and_failure(tmp_path):
    db = RunDB(tmp_path)
    with db.record("c", "unit", {"a": 1}, "h", {"git_sha": "x"}) as run:
        run["outputs"] = {"y": 2}
    with pytest.raises(RuntimeError):
        with db.record("c", "unit", {"a": 2}, "h2", {"git_sha": "x"}):
            raise RuntimeError("boom")
    rows = db.list("c")
    assert [r["status"] for r in rows] == ["ok", "failed"]
    got = db.get(rows[0]["run_id"])
    assert got["outputs"] == {"y": 2} and got["wall_time_s"] >= 0
    assert db.get(rows[1]["run_id"])["errors"]["message"] == "boom"
