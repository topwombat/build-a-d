"""NASA TM X-372 "arrow model" rebuilt for wave-drag validation (geometry in tmx372_arrow_geometry.yaml).

Holdaway & Mellenthin, NASA TM X-372 (1960): blended wing-body, aspect-ratio-2 arrow wing
(70.82 deg LE sweep), 60 in body of revolution, wind-tunnel zero-lift wave drag M 1.55-3.5.
Model-scale inches; coefficients on S = 800 in^2. Assumptions (flagged in the YAML or here):
- a constant-area sting continues aft of the 60 in base (the base is not closed);
  the cuts end on the sting (x_end = base), so only the forebody wave drag is counted,
  as in the report's measured forebody drag;
- the printed Table IV value at y = 6.667, x = 44.0 (0.371, a likely misprint) is used as printed.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from ssbj.disciplines.aero.wave_drag import harris_wave_drag
from ssbj.geometry.parametric import Aircraft, Body, Planform

GEOM = Path(__file__).parent / "tmx372_arrow_geometry.yaml"
# ASSUMPTION: constant-area sting aft of the base, long enough that every Mach-plane
# cut ends on it (harris_wave_drag x_end); the sting itself carries no wave drag.
STING_END_IN = 600.0


def build() -> tuple[Aircraft, dict]:
    g = yaml.safe_load(GEOM.read_text())
    st = [s for s in g["wing_stations"] if "semithickness" in s]  # the tip row has no section
    y = np.array([s["y"] for s in st], dtype=float)
    x_le = np.array([s["x_le"] for s in st], dtype=float)
    chord = np.array([s["chord"] for s in st], dtype=float)
    profiles, tcmax = [], []
    for s in st:
        tab = np.array(s["semithickness"], dtype=float)
        xi = (tab[:, 0] - s["x_le"]) / s["chord"]
        tc = 2.0 * tab[:, 1] / s["chord"]
        order = np.argsort(xi)
        profiles.append((xi[order], tc[order]))
        tcmax.append(float(tc.max()))
    # the pointed tip (x = 57.5, y = 20) closes the planform
    tip_y = g["reference"]["semispan_in"]
    if y[-1] < tip_y:
        y = np.append(y, tip_y)
        x_le = np.append(x_le, 57.5)
        chord = np.append(chord, 1e-6)
        profiles.append(profiles[-1])
        tcmax.append(tcmax[-1])
    wing = Planform(y, x_le, chord, np.array(tcmax), profiles)

    f = g["fuselage"]
    tab = np.array(f["radius_table"], dtype=float)
    x_nose, x_base, r_base = f["nose_x_in"], f["base_x_in"], f["base_radius_in"]

    def radius(xl):
        x = np.asarray(xl, dtype=float)
        r = np.interp(x, tab[:, 0], tab[:, 1])
        r = np.where(x < x_nose, 0.0, r)
        return np.where(x > x_base, r_base, r)  # sting

    body = Body("fuselage", 0.0, STING_END_IN, radius)
    ac = Aircraft(None, wing, body, None, [])
    return ac, g


def compare(machs) -> dict:
    ac, g = build()
    s_ref = g["reference"]["S_ref_in2"]
    data = {row[0]: row for row in g["measured_wave_drag"]["data"]}
    out = {}
    for m in machs:
        cd = harris_wave_drag(ac, m, x_end=g["fuselage"]["base_x_in"])["D_q"] / s_ref
        row = data[m]
        out[m] = {"model_cd": cd, "exp_cd": row[1], "theory_cd": row[2]}
    return out
