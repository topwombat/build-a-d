import copy

import pytest
import yaml
from pydantic import ValidationError

from ssbj.geometry.parametric import GeometryError, build
from ssbj.specs.schema import Case, numeric_leaves
from tests.conftest import CONCORDE


def _raw():
    return yaml.safe_load(CONCORDE.read_text())


def test_concorde_case_loads(concorde_case):
    assert concorde_case.validation_case
    assert concorde_case.mission.payload.mass_kg == pytest.approx(8845.0)


def test_validation_case_needs_provenance():
    d = _raw()
    del d["provenance"]["design.engine.lpc_pr"]
    with pytest.raises(ValidationError, match="design.engine.lpc_pr"):
        Case.model_validate(d)


def test_every_numeric_leaf_is_covered(concorde_case):
    assert len(numeric_leaves(concorde_case.model_dump(include={"mission", "design"}))) > 60


def test_profile_needs_one_cruise():
    d = _raw()
    d["mission"]["profile"] = [s for s in d["mission"]["profile"] if s["segment"] != "cruise"]
    with pytest.raises(ValidationError, match="cruise"):
        Case.model_validate(d)


def test_unknown_field_rejected():
    d = _raw()
    d["design"]["engine"]["bypass"] = 0.3
    with pytest.raises(ValidationError):
        Case.model_validate(d)


def test_concorde_geometry(concorde_aircraft):
    ac = concorde_aircraft
    assert ac.s_ref == pytest.approx(358.25, rel=1e-3)  # published gross area
    assert ac.wing.span == pytest.approx(25.6)
    assert ac.length == pytest.approx(61.66)
    assert ac.checks == ["nacelles: adjacent nacelles touch (paired installation)"] or ac.checks == []


@pytest.mark.parametrize("mutate,msg", [
    (lambda d: d["design"]["wing"]["stations"][0].update(y_m=1.0), "centreline"),
    (lambda d: d["design"]["nacelles"].update(y_m=[1.0, 6.3]), "fuselage"),
    (lambda d: d["design"]["nacelles"].update(y_m=[5.0]), "engine count"),
    (lambda d: d["design"]["fuselage"].update(nose_length_m=50.0), "nose"),
    (lambda d: d["design"]["fin"].update(x_le_root_m=5.0), "fin"),
    (lambda d: d["design"]["nacelles"].update(x_inlet_m=1.0), "overlap"),
])
def test_geometry_failures_detected(mutate, msg):
    d = copy.deepcopy(_raw())
    mutate(d)
    c = Case.model_validate(d)
    with pytest.raises(GeometryError, match=msg):
        build(c.design)


def test_area_distribution_at_mach_one_matches_volume(concorde_aircraft):
    """Normal-plane areas integrate to the component volumes (area-rule bookkeeping check)."""
    import numpy as np

    ac = concorde_aircraft
    x = np.linspace(-1, ac.length + 1, 2001)
    a = ac.mach_plane_areas(1.0, 0.0, x)
    vol_nac = sum(n.shell_area() * n.length * 0.75 for n in ac.nacelles) * 2  # cosine ramps: 3/4 of box
    # wing volume inside the fuselage is not counted twice: integrate it on an independent x-y grid
    w, b = ac.wing, ac.fuselage
    yy = np.linspace(0.0, w.y[-1], 300)
    xx = np.linspace(w.x_le.min(), (w.x_le + w.chord).max(), 3000)
    c = np.interp(yy, w.y, w.chord)
    xi = (xx[:, None] - np.interp(yy, w.y, w.x_le)[None, :]) / c[None, :]
    t = w.thickness(xi, yy) * c[None, :] * (yy[None, :] < b.radius(xx - b.x0)[:, None])
    inside = 2.0 * np.trapezoid(np.trapezoid(t, yy, axis=1), xx)
    expected = ac.fuselage.volume() + ac.wing.volume() - inside + ac.fin.volume() + vol_nac
    assert np.trapezoid(a, x) == pytest.approx(expected, rel=0.01)
