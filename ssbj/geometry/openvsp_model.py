"""Build the analysis geometry in OpenVSP and cross-check it.

OpenVSP (NASA Open Source Agreement 1.3) is optional at run time: it is built
from source in the container image (ssbj/docker/build_openvsp.sh) and used to
verify the in-house geometry and area-rule code, not to produce results.

Modelled: wing (biconvex sections, one OpenVSP panel per planform panel),
fuselage (circular sections sampled from the same radius law), fin. Nacelles
are left out of the cross-check because the two codes treat flow-through
bodies differently; the comparison uses the same subset on both sides.
"""
from __future__ import annotations

import numpy as np


def available() -> bool:
    try:
        import openvsp  # noqa: F401
    except Exception:
        return False
    return True


def build(ac, n_fus_sections: int = 24):
    import openvsp as vsp

    vsp.VSPRenew()
    w = ac.wing
    wid = vsp.AddGeom("WING")
    vsp.SetGeomName(wid, "wing")
    xs = vsp.GetXSecSurf(wid, 0)
    n_panels = len(w.y) - 1
    for _ in range(n_panels - 1):
        vsp.InsertXSec(wid, 1, vsp.XS_FOUR_SERIES)
    vsp.Update()
    for i in range(vsp.GetNumXSec(xs)):
        vsp.ChangeXSecShape(xs, i, vsp.XS_BICONVEX)
    vsp.Update()
    vsp.SetParmVal(wid, "X_Rel_Location", "XForm", float(w.x_le[0]))
    for i in range(n_panels):
        sec = f"XSec_{i + 1}"
        dy = float(w.y[i + 1] - w.y[i])
        vsp.SetDriverGroup(wid, i + 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
        vsp.SetParmVal(wid, "Span", sec, dy)
        vsp.SetParmVal(wid, "Root_Chord", sec, float(w.chord[i]))
        vsp.SetParmVal(wid, "Tip_Chord", sec, float(max(w.chord[i + 1], 1e-3)))
        vsp.SetParmVal(wid, "Sweep", sec, float(np.degrees(np.arctan2(w.x_le[i + 1] - w.x_le[i], dy))))
        vsp.SetParmVal(wid, "Sweep_Location", sec, 0.0)
        vsp.SetParmVal(wid, "Dihedral", sec, 0.0)
        vsp.Update()
    for i in range(n_panels + 1):
        vsp.SetParmVal(vsp.GetXSecParm(vsp.GetXSec(xs, i), "ThickChord"), float(w.tc[i]))
    vsp.Update()

    # fuselage
    fid = vsp.AddGeom("FUSELAGE")
    vsp.SetGeomName(fid, "fuselage")
    fus = ac.fuselage
    vsp.SetParmVal(fid, "Length", "Design", float(fus.length))
    fxs = vsp.GetXSecSurf(fid, 0)
    while vsp.GetNumXSec(fxs) < n_fus_sections:
        vsp.InsertXSec(fid, 1, vsp.XS_CIRCLE)
    vsp.Update()
    n = vsp.GetNumXSec(fxs)
    s = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))  # cluster stations at nose and tail
    # positions are clamped between neighbours: sweep backward and forward until they settle
    for _ in range(4):
        for i in list(range(n - 2, 0, -1)) + list(range(1, n - 1)):
            vsp.SetParmVal(vsp.GetXSecParm(vsp.GetXSec(fxs, i), "XLocPercent"), float(s[i]))
            vsp.Update()
    for i in range(1, n - 1):
        vsp.ChangeXSecShape(fxs, i, vsp.XS_CIRCLE)
        vsp.Update()
        sec = vsp.GetXSec(fxs, i)
        vsp.SetParmVal(vsp.GetXSecParm(sec, "Circle_Diameter"), float(2 * fus.radius(s[i] * fus.length)))
    vsp.Update()

    # fin
    f = ac.fin
    vid = vsp.AddGeom("WING")
    vsp.SetGeomName(vid, "fin")
    vxs = vsp.GetXSecSurf(vid, 0)
    for i in range(vsp.GetNumXSec(vxs)):
        vsp.ChangeXSecShape(vxs, i, vsp.XS_BICONVEX)
    vsp.Update()
    vsp.SetParmVal(vid, "Sym_Planar_Flag", "Sym", 0.0)
    vsp.SetParmVal(vid, "X_Rel_Rotation", "XForm", 90.0)
    vsp.SetParmVal(vid, "X_Rel_Location", "XForm", float(f.x_le_root))
    vsp.SetParmVal(vid, "Z_Rel_Location", "XForm", float(f.z_root))
    vsp.SetDriverGroup(vid, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
    vsp.SetParmVal(vid, "Span", "XSec_1", float(f.height))
    vsp.SetParmVal(vid, "Root_Chord", "XSec_1", float(f.root_chord))
    vsp.SetParmVal(vid, "Tip_Chord", "XSec_1", float(max(f.tip_chord, 1e-3)))
    vsp.SetParmVal(vid, "Sweep", "XSec_1", float(np.degrees(f.sweep_le)))
    vsp.SetParmVal(vid, "Sweep_Location", "XSec_1", 0.0)
    for i in range(vsp.GetNumXSec(vxs)):
        vsp.SetParmVal(vsp.GetXSecParm(vsp.GetXSec(vxs, i), "ThickChord"), float(f.tc))
    vsp.Update()
    return {"wing": wid, "fuselage": fid, "fin": vid}


def crosscheck(ac, machs=(1.2, 1.6, 2.0), n_slices: int = 60, n_rot: int = 12) -> dict:
    """Compare planform area, wetted areas and wave drag between OpenVSP and the in-house code.

    OpenVSP writes result files to the working directory, so this runs in a temporary one.
    """
    import os
    import tempfile

    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            return _crosscheck(ac, machs, n_slices, n_rot)
        finally:
            os.chdir(cwd)


def _crosscheck(ac, machs, n_slices, n_rot) -> dict:
    import copy

    import openvsp as vsp

    from ssbj.disciplines.aero.wave_drag import harris_wave_drag

    ids = build(ac)
    out = {"openvsp_version": vsp.GetVSPVersion()}
    out["wing_area"] = {"openvsp": vsp.GetParmVal(ids["wing"], "TotalArea", "WingGeom"),
                        "ssbj": ac.wing.area}
    rid = vsp.ExecAnalysis("CompGeom")
    names = vsp.GetStringResults(rid, "Comp_Name")
    wet = vsp.GetDoubleResults(rid, "Wet_Area")
    vols = vsp.GetDoubleResults(rid, "Wet_Vol")
    ours = ac.wetted_areas()
    out["wetted_m2"] = {n: {"openvsp": a, "ssbj": ours.get(n)} for n, a in zip(names, wet)}
    out["volume_m3"] = {n: v for n, v in zip(names, vols)}

    bare = copy.copy(ac)
    bare.nacelles = []
    vsp.SetAnalysisInputDefaults("WaveDrag")
    vsp.SetIntAnalysisInput("WaveDrag", "Set", [vsp.SET_ALL])
    vsp.SetIntAnalysisInput("WaveDrag", "NumSlices", [n_slices])
    vsp.SetIntAnalysisInput("WaveDrag", "NumRotSects", [n_rot])
    wd = {}
    for m in machs:
        vsp.SetDoubleAnalysisInput("WaveDrag", "Mach", [float(m)])
        r = vsp.ExecAnalysis("WaveDrag")
        cd = vsp.GetDoubleResults(r, "CDWave")[0]
        sref = _wave_sref()
        wd[f"M{m:g}"] = {"openvsp_D_q": cd * sref, "ssbj_D_q": harris_wave_drag(bare, m)["D_q"],
                         "openvsp_sref_used": sref}
    out["wave_drag_no_nacelles"] = wd
    return out


def _wave_sref() -> float:
    """Reference area OpenVSP's WaveDrag used for CDWave (its WaveDragSettings container)."""
    import openvsp as vsp

    cid = vsp.FindContainer("WaveDragSettings", 0)
    pid = vsp.FindParm(cid, "Sref", "WaveDrag")
    return vsp.GetParmVal(pid) if pid else float("nan")
