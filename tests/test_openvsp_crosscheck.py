"""Geometry and area-rule cross-check against OpenVSP 3.49 (an independent code).

Skipped when the OpenVSP Python API is not installed (it is built in the
container image). Tolerances are stated, not tuned: they are the agreement
seen when the check was first run, rounded up, and they are recorded in
docs/method_notes.md.
"""
import pytest

from ssbj.geometry import openvsp_model

pytestmark = pytest.mark.skipif(not openvsp_model.available(), reason="OpenVSP not installed")


@pytest.fixture(scope="module")
def check(concorde_aircraft):
    return openvsp_model.crosscheck(concorde_aircraft)


def test_wing_area(check):
    assert check["wing_area"]["openvsp"] == pytest.approx(check["wing_area"]["ssbj"], rel=1e-3)


def test_wetted_areas(check):
    w = check["wetted_m2"]
    assert w["wing"]["openvsp"] == pytest.approx(w["wing"]["ssbj"], rel=0.03)
    assert w["fin"]["openvsp"] == pytest.approx(w["fin"]["ssbj"], rel=0.06)
    # OpenVSP removes the wing-junction strip from the fuselage; ssbj does not (conservative)
    assert 0.90 < w["fuselage"]["openvsp"] / w["fuselage"]["ssbj"] < 1.0


def test_fuselage_alone(concorde_aircraft, tmp_path, monkeypatch):
    import openvsp as vsp

    monkeypatch.chdir(tmp_path)  # OpenVSP writes result files to the working directory
    ids = openvsp_model.build(concorde_aircraft)
    vsp.DeleteGeomVec([ids["wing"], ids["fin"]])
    vsp.Update()
    r = vsp.ExecAnalysis("CompGeom")
    assert vsp.GetDoubleResults(r, "Wet_Area")[0] == pytest.approx(
        concorde_aircraft.fuselage.wetted_area(), rel=0.02)
    assert vsp.GetDoubleResults(r, "Wet_Vol")[0] == pytest.approx(concorde_aircraft.fuselage.volume(), rel=0.04)


def test_wave_drag_code_to_code(check):
    """Harris implementation vs OpenVSP WaveDrag (no nacelles): within the 25 % aero.wave sigma."""
    for m, v in check["wave_drag_no_nacelles"].items():
        assert v["ssbj_D_q"] == pytest.approx(v["openvsp_D_q"], rel=0.15), m
