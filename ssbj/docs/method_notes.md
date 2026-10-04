# Method notes (Phase 1, low rung)

Every method below has a verification test (honesty rule 9). Equation numbers refer to
D. P. Raymer, *Aircraft Design: A Conceptual Approach*, 3rd ed., AIAA, 1999. A scan of it
is in the repository root; page numbers are those printed in the book.

## Geometry (`ssbj/geometry/parametric.py`)

- **Parameter vector.** The parameter vector covers the wing (piecewise-linear stations: y, x_LE, chord, t/c; parabolic-arc sections), the fuselage (length, diameter, power-law nose and tail), a trapezoidal fin, and rectangular nacelles with capture area.
- **Outputs.** Gross and exposed area, MAC, sweeps, wetted areas, volumes, and Mach-plane area distributions.
- **Failure detection.** A malformed parameter vector raises `GeometryError` with every failure listed (`ssbj validate <case>` reports them). The checks cover station ordering, non-positive chords, t/c range, a nose plus tail longer than the body, nacelle placement, and fin placement. Non-fatal findings go to `aircraft.checks`. Tests: `tests/test_schema_geometry.py`.
- **Cross-check against OpenVSP 3.49.0** (`ssbj/geometry/openvsp_model.py`, `tests/test_openvsp_crosscheck.py`), Concorde geometry:

| Quantity | OpenVSP | ssbj | Difference |
|---|---|---|---|
| Wing gross area | 358.25 m² | 358.25 m² | 0 |
| Wing wetted (exposed) | 551.6 m² | 545.7 m² | -1.1 % |
| Fin wetted | 71.0 m² | 67.9 m² | -4.3 % |
| Fuselage alone, wetted / volume | 506.6 m² / 352 m³ | 510.5 m² / 362 m³ | +0.8 % / +2.9 % |
| Fuselage in assembly, wetted | 481.0 m² | 510.5 m² | +6 % (OpenVSP removes the wing junction) |

## Aerodynamics (`ssbj/disciplines/aero`)

- **Skin friction.** Turbulent flat plate (eq. 12.27) with the cutoff Reynolds number for smooth paint (eqs. 12.28-12.29, Table 12.4). Subsonic form factors use eqs. 12.30-12.32; there are none supersonically (eq. 12.42).
- **Wave drag.** Harris far-field area rule: Mach-plane cuts at 24 roll angles, and the von Kármán integral by Fourier-sine fit.
  - Verified against the Sears-Haack closed form (eq. 12.45) to 1e-6 on aligned grids, and to O(dx/l) on misaligned ones.
  - Converged to within 2 % at 24 × 481.
  - **Code-to-code against OpenVSP WaveDrag** (Concorde, no nacelles): ssbj is 9-11 % higher at M 1.2-2.0. Phase 1 accepts this inside the 25 % `aero.wave` sigma. The cause is not yet resolved; candidates are the thin-wing slicing and OpenVSP's slice count.
  - The Raymer eq. 12.46 empirical correlation is reported in every run. It sits at about half the Harris value for Concorde. That is a known weakness of the correlation for this configuration, and the run warns.
- **Lift.** CL_alpha uses eq. 12.6 subsonically and Jones/Stewart linear theory for a delta of equal AR supersonically (verified limits πAR/2 and 4/β). K comes from the leading-edge-suction method with S = 0.2 (assumed).

## Propulsion (`ssbj/disciplines/propulsion`)

- **Cycle.** pyCycle afterburning turbojet (adapted from pyCycle `example_cycles`, Apache-2.0): AXI5 compressor map, LPT2269 turbine map, tabular Jet-A thermo.
- **Deck.** 14 Mach × 14 altitude × 8 dry settings + full reheat, solved with continuation; about 15 minutes on 4 cores. It is cached by a hash of the generation code (`decks/`). Reheat uses a secant on afterburner FAR, because an in-cycle balance diverged.
- **Envelope and convergence.** Points above q = 120 kPa, or slow at high altitude, are not solved. In-envelope failures are filled from the nearest altitude and counted in run warnings.
- **Installation.** Inlet recovery follows MIL-E-5008B as cited by Raymer App. A.4. The schedule formula (1 − 0.075 (M − 1)^1.35) was entered from general knowledge and still needs checking against the specification text.
- **Weight.** Engine weight uses Raymer eqs. 10.1-10.3 scaled from App. A.4-1 (30,000 lbf, 3,000 lb).

## Weights (`ssbj/disciplines/weights/raymer_transport.py`)

- **Equations.** Raymer cargo/transport eqs. 15.25-15.44 (pp. 403-404), terminology pp. 405-407, and Table 15.3 for seats and lavatories.
- **No calibration factors.** Raymer §15.4 recommends class "fudge factors" from a similar aircraft. Applying them to Concorde would break blind reproduction, so none are used.
- **Test.** Eq. 15.25 is re-evaluated by hand from the recorded inputs.

## Mission (`ssbj/disciplines/mission/analysis.py`)

- **Segments.** Energy-method climbs and accelerations along prescribed (Mach, altitude) lines; cruise-climb at best specific range within the altitude band; idle descent.
- **Reserves.** Contingency, a diversion flown as level cruise, and a hold.
- **Verified** against the Breguet range equation for constant L/D and TSFC (`tests/test_mission_breguet.py`, 0.1 %).

## Uncertainty (`ssbj/model/uncertainty.py`)

- **Sampling.** Monte Carlo over every declared factor: 200 samples, a fixed seed, 4 processes.
- **Correlations.** None, except the shared `weights.class_structure` factor.
- **Infeasible samples.** Samples that cannot fly the profile are counted and reported. Percentiles are conditional on feasibility (decision D-013).

## Tool check at setup (2026-10-04)

| Tool | Version found | Licence | Maintenance | Headless here |
|---|---|---|---|---|
| OpenMDAO | 3.45.1 (PyPI, 2026-09-11) | Apache-2.0 | active | yes |
| pyCycle | 4.4.0 PyPI (2025-10-15); git ee7e161 used (2026-05-20) | Apache-2.0 (repo LICENSE.txt) | active, but PyPI lags numpy 2 | yes |
| OpenVSP | 3.49.0 (git tag), built from source | NOSA 1.3 | active | yes, about 10 min no-graphics build |
| SU2 | v8.5.0 (git tag; last commit 2026-04-28) | LGPL-2.1 | active | not installed (Phase 4) |
| OpenAeroStruct | 2.12.0 (PyPI, 2025-10-06) | as listed on PyPI; repo moved from OpenMDAO/OpenAeroStruct (needs checking) | active | not installed (Phase 4) |
| TACS | v3.12.3 (git tag; last commit 2026-09-11) | Apache-2.0 | active | not installed (Phase 4) |
| Aviary | v1.0.2 (git tag; last commit 2026-09-29); PyPI om-aviary 0.9.9 lags | Apache-2.0 (NASA) | active | not installed |

Export-control status of every tool is **not** established here. It must be confirmed by the owner's counsel, as the brief says.
