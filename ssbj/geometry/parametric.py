"""Parametric analysis geometry driven from a parameter vector.

This is the geometry every Phase 1 discipline reads: planform properties,
wetted areas, volumes and Mach-plane area distributions for the supersonic
area rule. When the OpenVSP Python API is installed, ``openvsp_model.build``
creates the same configuration in OpenVSP and the tests cross-check wetted
areas and volumes against it (see docs/known_limits.md, "geometry").

Conventions: SI units, x aft from the fuselage nose, y to starboard, z up.
The configuration is symmetric about y = 0; wing and nacelle data describe
the starboard side.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ssbj.specs.schema import Design


class GeometryError(ValueError):
    """Raised when a parameter vector does not describe a valid aircraft."""

    def __init__(self, failures: list[str]):
        self.failures = failures
        super().__init__("; ".join(failures))


@dataclass
class Planform:
    y: np.ndarray  # spanwise stations, starboard, m (first station at y = 0)
    x_le: np.ndarray  # leading-edge x at each station, m
    chord: np.ndarray  # m
    tc: np.ndarray  # thickness/chord at each station

    @property
    def span(self) -> float:
        return 2.0 * float(self.y[-1])

    @property
    def area(self) -> float:
        """Gross (reference) planform area including the part inside the fuselage."""
        return 2.0 * float(np.trapezoid(self.chord, self.y))

    @property
    def aspect_ratio(self) -> float:
        return self.span**2 / self.area

    @property
    def mac(self) -> float:
        return 2.0 * float(np.trapezoid(self.chord**2, self.y)) / self.area

    def le_sweep_area_weighted(self) -> float:
        """Leading-edge sweep (rad), weighted by panel area."""
        dy = np.diff(self.y)
        sweep = np.arctan2(np.diff(self.x_le), dy)
        w = 0.5 * (self.chord[1:] + self.chord[:-1]) * dy
        return float(np.sum(sweep * w) / np.sum(w))

    def sweep_at(self, frac: float) -> float:
        """Area-weighted sweep (rad) of the line at chord fraction ``frac``."""
        x = self.x_le + frac * self.chord
        dy = np.diff(self.y)
        sweep = np.arctan2(np.diff(x), dy)
        w = 0.5 * (self.chord[1:] + self.chord[:-1]) * dy
        return float(np.sum(sweep * w) / np.sum(w))

    def exposed_area(self, y_root: float) -> float:
        """Planform area outboard of y_root, both sides."""
        yy = np.linspace(y_root, self.y[-1], 400)
        return 2.0 * float(np.trapezoid(np.interp(yy, self.y, self.chord), yy))

    def volume(self, y_from: float = 0.0, chord_from: float = 0.0, chord_to: float = 1.0) -> float:
        """Enclosed volume (both sides) of a parabolic-arc section between chord fractions.

        Section thickness distribution t(xi) = 4 t_max xi (1 - xi); the area
        between xi_a and xi_b is t_max c * 4 [xi^2/2 - xi^3/3].
        """
        def frac(a, b):
            f = lambda s: s**2 / 2 - s**3 / 3
            return 4.0 * (f(b) - f(a))

        yy = np.linspace(y_from, self.y[-1], 400)
        c = np.interp(yy, self.y, self.chord)
        tc = np.interp(yy, self.y, self.tc)
        return 2.0 * float(np.trapezoid(tc * c**2 * frac(chord_from, chord_to), yy))


@dataclass
class Body:
    """Body of revolution described by a radius distribution."""

    name: str
    x0: float
    length: float
    radius_fn: object  # callable: local x in [0, length] -> radius (m)
    y: float = 0.0
    z: float = 0.0

    def radius(self, x_local):
        x_local = np.asarray(x_local, dtype=float)
        r = np.where((x_local >= 0) & (x_local <= self.length), self.radius_fn(np.clip(x_local, 0, self.length)), 0.0)
        return r

    def area_at(self, x):
        return np.pi * self.radius(np.asarray(x) - self.x0) ** 2

    def wetted_area(self, n: int = 600) -> float:
        x = np.linspace(0, self.length, n)
        r = self.radius(x)
        ds = np.sqrt(np.diff(x) ** 2 + np.diff(r) ** 2)
        return float(np.sum(np.pi * (r[1:] + r[:-1]) * ds))

    def volume(self, n: int = 600) -> float:
        x = np.linspace(0, self.length, n)
        return float(np.trapezoid(np.pi * self.radius(x) ** 2, x))

    def max_area(self) -> float:
        x = np.linspace(0, self.length, 600)
        return float(np.max(np.pi * self.radius(x) ** 2))


@dataclass
class Nacelle:
    """Rectangular-section nacelle (one per engine) with internal flow.

    For wave drag only the external shell is counted: the streamtube entering
    the capture area is subtracted, and the shell area is ramped to zero over
    the first and last ``ramp`` fraction of the length (the exhaust jet is
    assumed to fill the nozzle exit). See docs/known_limits.md.
    """

    x0: float
    y: float
    z: float
    length: float
    width: float
    height: float
    capture_area: float
    ramp: float = 0.25

    def shell_area(self) -> float:
        return max(self.width * self.height - self.capture_area, 0.0)

    def area_at(self, x):
        xl = (np.asarray(x, dtype=float) - self.x0) / self.length
        r = self.ramp
        a = np.clip(np.minimum(xl / r, (1.0 - xl) / r), 0.0, 1.0)
        a = 0.5 - 0.5 * np.cos(np.pi * a)  # smooth ramps (zero slope at ends)
        return self.shell_area() * a

    def wetted_area(self) -> float:
        return 2.0 * (self.width + self.height) * self.length

    @property
    def fineness(self) -> float:
        d = np.sqrt(4.0 * self.width * self.height / np.pi)
        return self.length / d


@dataclass
class Fin:
    """Vertical tail on the centreline: trapezoid in the x-z plane."""

    x_le_root: float
    z_root: float
    root_chord: float
    tip_chord: float
    height: float
    sweep_le: float  # rad
    tc: float

    @property
    def area(self) -> float:
        return 0.5 * (self.root_chord + self.tip_chord) * self.height

    @property
    def aspect_ratio(self) -> float:
        return self.height**2 / self.area

    @property
    def mac(self) -> float:
        lam = self.tip_chord / self.root_chord
        return 2 / 3 * self.root_chord * (1 + lam + lam**2) / (1 + lam)

    def sweep_quarter(self) -> float:
        x_tip_qc = self.height * np.tan(self.sweep_le) + 0.25 * self.tip_chord
        return float(np.arctan2(x_tip_qc - 0.25 * self.root_chord, self.height))

    def volume(self) -> float:
        # parabolic arc: section area = (2/3) t c
        zz = np.linspace(0, self.height, 100)
        c = self.root_chord + (self.tip_chord - self.root_chord) * zz / self.height
        return float(np.trapezoid(2.0 / 3.0 * self.tc * c**2, zz))


@dataclass
class Aircraft:
    design: Design
    wing: Planform
    fuselage: Body
    fin: Fin
    nacelles: list[Nacelle]
    checks: list[str] = field(default_factory=list)  # non-fatal geometry warnings

    # ---- derived quantities used by the disciplines ----
    @property
    def s_ref(self) -> float:
        return self.wing.area

    @property
    def fuselage_radius_at_wing(self) -> float:
        return float(self.fuselage.radius(self.wing.x_le[0] + 0.5 * self.wing.chord[0] - self.fuselage.x0))

    @property
    def length(self) -> float:
        xs = [self.fuselage.x0 + self.fuselage.length,
              float(np.max(self.wing.x_le + self.wing.chord)),
              self.fin.x_le_root + self.fin.root_chord]
        xs += [n.x0 + n.length for n in self.nacelles]
        return max(xs)

    def wetted_areas(self) -> dict[str, float]:
        r = self.fuselage_radius_at_wing
        s_exp = self.wing.exposed_area(r)
        tc_mean = float(np.mean(self.wing.tc))
        # Raymer (1999) eq. 7.11-7.12 style planform-to-wetted factor: 2.003 for t/c < 0.05
        k_wing = 2.003 if tc_mean < 0.05 else 1.977 + 0.52 * tc_mean
        k_fin = 2.003 if self.fin.tc < 0.05 else 1.977 + 0.52 * self.fin.tc
        return {
            "wing": k_wing * s_exp,
            "fuselage": self.fuselage.wetted_area(),
            "fin": k_fin * self.fin.area,
            "nacelles": sum(n.wetted_area() for n in self.nacelles) * 2,  # both sides
        }

    def component_lengths(self) -> dict[str, float]:
        return {
            "wing": self.wing.mac,
            "fuselage": self.fuselage.length,
            "fin": self.fin.mac,
            "nacelles": self.nacelles[0].length if self.nacelles else 0.0,
        }

    def wing_fuel_volume(self) -> float:
        """Internal wing volume between 10 % and 75 % chord outboard of the fuselage side.

        Ogee/delta SST wings carry fuel across most of the chord; this box is a
        conservative usable-volume proxy. Fuselage trim tanks are not counted.
        """
        return self.wing.volume(self.fuselage_radius_at_wing, 0.10, 0.75)

    # ---- supersonic area rule ----
    def mach_plane_areas(self, mach: float, theta: float, x0: np.ndarray, ny: int = 161, nz: int = 61) -> np.ndarray:
        """Area intercepted by the Mach plane x = x0 + B (y cos th + z sin th), projected on the y-z plane.

        Returns the intercepted area for each value in ``x0`` (both sides of the aircraft).
        B = sqrt(M^2 - 1); for M = 1 the planes are normal cuts.
        """
        B = np.sqrt(max(mach**2 - 1.0, 0.0))
        ct, st = np.cos(theta), np.sin(theta)
        x0 = np.asarray(x0, dtype=float)
        total = np.zeros_like(x0)

        # wing (thin-wing approximation, both halves): integrate thickness along the cut line in z = 0
        w = self.wing
        for side in (1.0, -1.0):
            yy = np.linspace(0.0, w.y[-1], 400)
            xle = np.interp(yy, w.y, w.x_le)
            c = np.interp(yy, w.y, w.chord)
            tc = np.interp(yy, w.y, w.tc)
            dy = yy[1] - yy[0]
            xc = x0[:, None] + B * side * yy[None, :] * ct
            xi = (xc - xle[None, :]) / c[None, :]
            t = np.where((xi >= 0) & (xi <= 1), 4.0 * tc[None, :] * c[None, :] * xi * (1 - xi), 0.0)
            total += np.trapezoid(t, dx=dy, axis=1)

        # fin (thin, in x-z plane at y = 0): cut line x = x0 + B z sin(th)
        f = self.fin
        zz = np.linspace(0.0, f.height, 120)
        xle = f.x_le_root + zz * np.tan(f.sweep_le)
        c = f.root_chord + (f.tip_chord - f.root_chord) * zz / f.height
        xc = x0[:, None] + B * (f.z_root + zz[None, :]) * st
        xi = (xc - xle[None, :]) / c[None, :]
        t = np.where((xi >= 0) & (xi <= 1), 4.0 * f.tc * c[None, :] * xi * (1 - xi), 0.0)
        total += np.trapezoid(t, zz, axis=1)

        # fuselage: area of the oblique cut through a body of revolution, numerically on a y-z grid
        b = self.fuselage
        rmax = float(np.max(b.radius(np.linspace(0, b.length, 400))))
        ys = np.linspace(-rmax, rmax, ny)
        zs = np.linspace(-rmax, rmax, nz * 2)
        Y, Z = np.meshgrid(ys, zs, indexing="ij")
        cell = (ys[1] - ys[0]) * (zs[1] - zs[0])
        xcut = x0[:, None, None] + B * (Y[None] * ct + Z[None] * st)
        rr = b.radius(xcut - b.x0)
        total += np.sum((Y[None] ** 2 + Z[None] ** 2) <= rr**2, axis=(1, 2)) * cell

        # nacelles (both sides): shell area evaluated where the plane crosses the nacelle axis
        for n in self.nacelles:
            for side in (1.0, -1.0):
                total += n.area_at(x0 - B * (side * n.y * ct + n.z * st))
        return total


def _fuselage_body(d: Design) -> Body:
    f = d.fuselage
    R = f.max_diameter_m / 2.0
    Ln, Lt, L = f.nose_length_m, f.tail_length_m, f.length_m
    r_end = f.tail_end_diameter_m / 2.0

    def r(x):
        x = np.asarray(x, dtype=float)
        nose = R * np.clip(1.0 - (1.0 - np.clip(x / Ln, 0, 1)) ** 2, 0, 1) ** 0.75
        s = np.clip((x - (L - Lt)) / Lt, 0, 1)
        tail = r_end + (R - r_end) * np.clip(1.0 - s**2, 0, 1) ** 0.75
        return np.where(x < Ln, nose, np.where(x > L - Lt, tail, R))

    return Body("fuselage", 0.0, L, r)


def build(design: Design) -> Aircraft:
    """Build the analysis geometry from the design vector and check it.

    Raises GeometryError listing every failure found; returns the aircraft with
    non-fatal warnings in ``.checks`` otherwise.
    """
    fails: list[str] = []
    warns: list[str] = []
    w = design.wing
    st = sorted(w.stations, key=lambda s: s.y_m)
    y = np.array([s.y_m for s in st])
    planform = Planform(
        y=y,
        x_le=np.array([s.x_le_m for s in st]),
        chord=np.array([s.chord_m for s in st]),
        tc=np.array([s.tc for s in st]),
    )
    if y[0] != 0.0:
        fails.append("wing: first station must be at y = 0 (centreline)")
    if np.any(np.diff(y) <= 0):
        fails.append("wing: station y values must be strictly increasing")
    if np.any(planform.chord[:-1] <= 0) or np.any(planform.chord < 0):
        fails.append("wing: chords must be positive (tip chord may be zero)")
    if np.any((planform.tc < 0.01) | (planform.tc > 0.20)):
        fails.append("wing: t/c outside 0.01-0.20")

    fus = _fuselage_body(design)
    f = design.fuselage
    if f.nose_length_m + f.tail_length_m > f.length_m:
        fails.append("fuselage: nose + tail length exceeds fuselage length")
    if f.length_m / f.max_diameter_m < 5:
        warns.append("fuselage: fineness ratio < 5, outside slender-body assumptions")

    v = design.fin
    fin = Fin(v.x_le_root_m, f.max_diameter_m / 2.0, v.root_chord_m, v.tip_chord_m, v.height_m,
              np.radians(v.sweep_le_deg), v.tc)
    if v.tip_chord_m > v.root_chord_m or v.height_m <= 0:
        fails.append("fin: invalid trapezoid (tip chord > root chord or non-positive height)")

    nac = []
    n = design.nacelles
    for yi in n.y_m:
        nac.append(Nacelle(n.x_inlet_m, yi, n.z_m, n.length_m, n.width_m, n.height_m, n.capture_area_m2))
    if len(n.y_m) * 2 != design.engine.count:
        fails.append(f"nacelles: {len(n.y_m)} starboard nacelles but engine count is {design.engine.count}")
    if n.capture_area_m2 >= n.width_m * n.height_m:
        fails.append("nacelles: capture area must be smaller than nacelle frontal area")

    ac = Aircraft(design, planform, fus, fin, nac, warns)
    if not fails:
        # placement checks (need the assembled aircraft)
        if planform.x_le[0] < 0 or planform.x_le[0] + planform.chord[0] > f.length_m:
            fails.append("wing: root chord extends beyond the fuselage")
        r_w = ac.fuselage_radius_at_wing
        if r_w >= planform.y[-1]:
            fails.append("wing: semispan does not reach outside the fuselage")
        for k in nac:
            if not (0 < k.y < planform.y[-1]):
                fails.append("nacelles: spanwise position outside the wing")
            else:
                xle = float(np.interp(k.y, planform.y, planform.x_le))
                c = float(np.interp(k.y, planform.y, planform.chord))
                if k.x0 + k.length < xle or k.x0 > xle + c:
                    fails.append("nacelles: nacelle does not overlap the local wing chord")
            if k.y - k.width / 2 < r_w:
                fails.append("nacelles: nacelle intersects the fuselage")
        if len(nac) > 1:
            gaps = np.diff(sorted(k.y for k in nac))
            if np.any(gaps < n.width_m * 0.999):
                warns.append("nacelles: adjacent nacelles touch (paired installation)")
        if fin.x_le_root + fin.root_chord > f.length_m + 1e-6:
            warns.append("fin: root trailing edge aft of fuselage end")
        if fin.x_le_root < f.length_m * 0.5:
            fails.append("fin: root leading edge ahead of fuselage mid-length")
    if fails:
        raise GeometryError(fails)
    return ac
