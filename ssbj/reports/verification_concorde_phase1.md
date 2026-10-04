# Independent verification: Concorde Phase 1 case

Verifier: an independent agent that did not write or run this case before. Date: 2026-10-04.
Subject: `ssbj/validation/concorde/case.yaml`, run `20261004T224030-4bbc81` (code `aa5fc4a`), report `ssbj/reports/concorde_run_20261004T224030.md`.

**Verdict: REPRODUCED, BUT THE PASS IS WEAK AND OVERSTATED.** The numbers reproduce exactly, and the core physics (atmosphere, Raymer equations, units, reference area, fuel accounting) checks out. However:

- one Monte Carlo defect biases the range interval upward;
- two declared mechanisms do not exist (the `mission.integration` factor and the "step-halving check");
- one Raymer input is misread (furnishings);
- the README claims an independent verification that had not happened.

On substance, the gates pass only because large errors cancel. Put the engine mass or the OEW at its published value, with everything else unchanged, and the model cannot fly the 3,550 nmi mission at all. The gate as built does not show that the method reproduces Concorde.

## What I reproduced

| Check | Result |
|---|---|
| `SSBJ_RUNS_DIR=/tmp/verify_runs python -m ssbj run ssbj/validation/concorde/case.yaml --samples 200` (my run `20261004T230648-e07f5c`, code `e0d945b`, clean tree) | The nominal results and every Monte Carlo statistic are **bit-identical** to the recorded run: range 3,481 nmi (95 % 3,220-5,208), fuel 98,128 kg (62,342-107,978), 82/200 infeasible (65 of them in supersonic_climb). |
| `python -m pytest -q tests` | 46 passed in 193 s. This does **not** run the acceptance test `ssbj/validation/test_concorde.py`; only bare `pytest` picks up `testpaths`. I re-ran the case directly instead. |
| Atmosphere (`ssbj/core/atmosphere.py`) against USSA-1976 table values at 0, 11, 15.24, 20 and 25 km | T exact; p and rho within 2e-5. |
| Cruise point by hand (M2, 50,000 ft, 125.5 t) | q 32.47 kPa, CL 0.106, CD 0.01586 (friction 0.00540, misc 0.00027, wave 0.00497, lift 0.00521), L/D 6.67, D 184.5 kN, TSFC 1.120 /h (max dry 186.9 kN). The Breguet estimate for the cruise leg is 1,484 nmi against 1,475 integrated. |
| CD reference area | Polar, geometry and mission all use 358.2507 m² (friction, wave drag and CL are all on `s_ref`). Consistent. |
| TSFC / fuel-flow units (`deck.py:321-334, 367-368`) | Fuel flow is in kg/s and thrust in N; TSFC = ff·g/F·3600 in 1/h. Correct. In `fuel_flow_at_thrust`, the thrust factor scales thrust and fuel flow together, so it keeps SFC fixed; the SFC factor is applied separately. Consistent. |
| Fuel accounting (`analysis.py`) | Range = climb + cruise + descent distances: 86.3 + 76.0 + 1,720.9 + 1,474.6 + 123.0 = 3,480.8 nmi. Take-off and taxi cover no distance (a conservative choice). Trip fuel excludes taxi (75,639 = 76,792 − 769 − 385). Ramp fuel = block + reserves (76,792 + 18,888 = 95,680). The `fly_range` residual is −0.4 kg. I found no sign errors, no double-counted reserves and no omitted reserves. |
| Integration step | Doubling the steps changes range by +0.10 % and fuel by −0.14 %. Halving them changes range by −0.20 % and fuel by +0.28 %. Converged. |
| Raymer eqs. 15.25-15.44 against the scan (book pp. 403-407, PDF pp. 211-213) | Every coefficient and exponent matches. Units are right: lb, ft, ft², gal, and inches for the gear lengths, with Nz = 1.5 × limit. The two exceptions are the furnishings input (defect 3) and the minor points below. |
| Blind-reproduction history | See below. Sigmas were committed in bf5c882 before results. The engine deck `fn`/`ff` arrays are bit-identical from bf5c882 through aa5fc4a. |

## Confirmed defects (ranked)

### 1. (High) The Monte Carlo drops valid range samples whenever the *other* mission fails

**Where:** `ssbj/model/uncertainty.py:248-255`.

**What happens:** `_one` wraps both `fly_range` (the range gate) and `fly_distance` (the 3,550 nmi fuel gate) in a single `analyse` call. A sample is therefore discarded from **every** statistic if either mission is infeasible.

**Effect on this run:** re-running the same 200 seeded samples with the two missions separated:

- 144 samples can fly the max-fuel range mission; only 118 can fly both.
- 26 samples have a valid max-fuel range of **2,059-3,379 nmi**, every one of them below the published 3,550. They are excluded only because they cannot fly 3,550 nmi.
- I probed four of them. Their range rises with fuel, then hits a climb infeasibility before reaching 3,550 nmi, so their design-mission failure is genuine. Their range values are still valid data.

The filter removes exactly the samples that argue against the range gate:

| Range percentiles (nmi) | p2.5 | p16 | p50 | p84 | p97.5 |
|---|---|---|---|---|---|
| Reported (both missions feasible, n = 118) | 3,220 | 3,513 | 3,897 | 4,488 | 5,208 |
| Range-mission feasible (n = 144) | **2,562** | **3,225** | 3,752 | 4,401 | 5,163 |
| Unconditional, infeasible counted as 0 | 0 | 0 | 3,500 | 4,252 | 5,105 |

The gate still passes either way. But the reported lower bound is 660 nmi too high. Also, 81 % of the reported feasible samples exceed 3,550, against 47.5 % unconditionally.

**A related fragility:** the secant search in `fly_distance` (`analysis.py:288-301`) has no bracketing and no feasibility handling. Any probe that strays into an infeasible weight raises, and the sample is lost. Of the 81 design-mission failures, 30 are "fuel does not cover the non-cruise segments" errors raised during this search.

### 2. (Medium) The `mission.integration` factor is sampled but never applied, and the "step-halving check" does not exist

**Where:** `ssbj/disciplines/mission/analysis.py:28-31`.

- The factor is declared at 1 % and listed under "Error factors sampled" in the run report, and in `docs/known_limits.md`.
- Its basis reads "Step-halving check on the integration; reported per case".
- No code calls `f("mission.integration")`, and no step-halving check exists anywhere (grep for `halv`).
- **Failing example:** `Factors({"mission.integration": 1.5})` gives range 3,480.68 nmi and fuel 98,128.4 kg, identical to nominal.

The numerical effect is negligible: I measured the step error at 0.2 % or less. The problem is that the documentation and the report describe an error source and a check that are not there.

### 3. (Low-medium) Furnishings uses mission cargo in place of Raymer's "maximum cargo weight"

**Where:** `ssbj/disciplines/weights/raymer_transport.py:135-136`.

- Raymer p. 407 defines W_c as the *maximum cargo weight* (lb).
- The code uses `payload.cargo_kg` (0 for this mission) clipped to 1 lb.
- Result: furnishings (eq. 15.41) = **20.8 kg**.
- With an illustrative W_c of 4,535 kg (the Heritage max payload of 13,380 kg minus the 8,845 kg passenger load), the same equation gives **777 kg**.
- So OEW is about 0.75 t low, worth roughly +30 nmi of range, a bias in the passing direction.
- The fix needs a design-definition field (maximum cargo), not a mission field.

### 4. (Medium, honesty) The README claims a verification that had not happened

**Where:** `ssbj/README.md:56`.

The row reads "No self-grading | An independent verifier agent re-ran and checked the case (see `reports/concorde_phase1.md`)". That file does not exist in any commit. When the README was committed (2ab66a7 / aa5fc4a) no verification had been completed; the first attempt was lost. The claim should be removed until this report, or a successor, is accepted.

### 5. (Low) `prop.weight` does not reach engine-dependent groups

**Where:** `raymer_transport.py:93, 124`.

The nacelle group (via W_ec) and the starter use the nominal engine weight. Only the `engines` line is scaled by `prop.weight` (line 148), so the sampled engine-weight error is slightly under-propagated.

### 6. (Low) `fly_range` accepts a non-converged result silently

**Where:** `analysis.py:275-286`.

After 30 iterations the last state is returned without any warning. Nominal converges (residual 0.4 kg), so this is latent.

Minor Raymer-terminology deviations, each with negligible effect:

- L uses total fuselage length, where Raymer specifies structural length.
- I_y uses a 0.3 L radius, where Raymer's terminology gives K_z ≈ L_t (exponent 0.07).
- N_c = 9 (unverified, including cabin crew) feeds instruments and furnishings.

## Blind-reproduction integrity (item 3)

- **Sigmas committed before results.** In `git log -p`, bf5c882 (21:40) contains every sigma. Between bf5c882 and aa5fc4a the only sigma change is the removal of `weights.engines` (D-012). That removal was a genuine double count with `prop.weight`, and no value changed. The 25 % `aero.wave` sigma and its later justification ("ssbj is 9-11 % higher than OpenVSP") are consistent.
- **Inputs changed after the first Concorde result:**
  - **D-009: take-off end state moved from M0.3 to M0.4 / 1,500 ft.** I re-flew the alternatives:

    | Take-off end Mach | Range (nmi) | 3,550 nmi mission |
    |---|---|---|
    | 0.30 | infeasible | infeasible |
    | 0.35 | 3,399 | infeasible |
    | 0.40 (chosen) | 3,481 | 98,128 kg |
    | 0.45 | 3,516 | 96,838 kg |
    | 0.50 | 3,538 | 96,059 kg |

    M0.4 is the lowest grid value at which both missions fly. It is not the value that best matches 3,550. This looks like a feasibility fix, not tuning. But the take-off allowance gives free kinetic energy at no distance, and range moves about 35 nmi per 0.05 of end Mach. Thirteen samples still fail at M0.41 just after the allowance.
  - **D-016: control-surface area 36 → 42.4 m²** (sourced). By the exponents (0.1 on the wing, 0.2 on flight controls) this adds about 0.53 t to OEW and costs about 20 nmi of range, which moves the model *away* from 3,550. Not tuning.
  - **D-012:** a sigma-list change only.
- **Gate reference values** (3,550 nmi, 95,680 kg) are unchanged since bf5c882. The engine deck is bit-identical.
- **Published figures as inputs.** No predicted performance figure (OEW, SFC, L/D, engine mass) is a model input; grep of the code and the case confirms this. However, the gate condition is built from published figures:
  - `design_range_nmi: 3550` is the published range itself, used as the distance for the fuel gate.
  - `fuel_capacity_kg: 95680` is the published max-fuel figure, used as both the input fuel load for the range gate and the reference value of the fuel gate.
  - `mass_per_passenger_kg` is derived from the published 8,845 kg payload.

  This is legitimate by D-005 and D-014, but it means the "fuel for 3,550 nmi" gate is the range gate inverted: design fuel > capacity exactly when range < 3,550. **There is one gate, not two.**
- T4 and the afterburner temperature are matched to the published airflow and reheat thrust (design data, per D-006). This is acceptable. Note that the airflow figure has no stated condition.

## Is "PASS" meaningful? (item 4)

1. **The interval is very wide.**
   - Range: 3,220-5,208 nmi, i.e. −7 % to +50 % about nominal and 57 % of the published value in width.
   - Fuel: 62.3-108.0 t, 48 % of published.
   - Any published range between 3,220 and 5,208 nmi, or any fuel load between 62 and 108 t, would have passed.
2. **Conditioning selects favourable aircraft.**
   - Feasible samples have systematically lower drag and weight factors than infeasible ones:

     | Factor | Feasible mean | Infeasible mean |
     |---|---|---|
     | `aero.wave` | 0.94 | 1.12 |
     | `aero.K` | 0.94 | 1.06 |
     | `weights.wing` | 0.91 | 1.12 |

   - The +416 nmi gap between the feasible median (3,897) and nominal (3,481) is the selection effect, not nonlinearity: the unconditional median is 3,500.
   - With 41 % of samples unable to fly, the honest unconditional lower bound is "cannot fly the mission".
3. **The model aircraft barely reaches Mach 2.**
   - Nominal supersonic climb (M1.7 / 43 kft to M2.0 / 50 kft) takes 95.5 min, 1,721 nmi and 36.7 t of fuel, with a minimum Ps of 0.86 m/s. At 160 t, max dry thrust is below drag from M1.85 upward.
   - Before cruise, the model burns 67 % of trip fuel and covers 54 % of the distance. ICAS 1976 (quoted in the case's own `VERIFICATION.md`) says 20 % and 9 %. The model's cruise is a third of the flight rather than the bulk of it.
   - Range is therefore extremely sensitive to the thrust/drag balance at M1.7-2.0. With `prop.thrust` at 0.95 (one sigma), the 3,550 nmi mission becomes infeasible.
   - The run report does not mention any of this.
4. **The errors compensate.** I re-flew the nominal mission with single quantities set to their published values:

   | Change (all else nominal) | Range at max fuel | Fuel for 3,550 nmi |
   |---|---|---|
   | Nominal (OEW 72.4 t, engine 1.77 t, TSFC 1.12, L/D 6.63) | 3,481 nmi | 98.1 t |
   | Engine mass 3,175 kg each (OEW becomes 78.9 t, ≈ the published 78.7 t) | 3,230 nmi | **infeasible** |
   | OEW = 78.7 t (published) | 3,239 nmi | **infeasible** |
   | SFC × 1.067 (TSFC → published 1.195) | 3,193 nmi | 110.6 t |
   | OEW 78.7 t and TSFC 1.195 | 2,965 nmi | **infeasible** |
   | `aero.wave` × 0.75 or `aero.K` × 0.85 (L/D toward 7.1-7.5) | 3,834 / 3,868 nmi | 87.1 / 86.5 t |

   - The 6.3 t OEW deficit is almost entirely the engine-mass error (−44 %, outside the declared 30 % sigma in the direction the basis already says is biased).
   - The low TSFC and low OEW offset an L/D that is 7-12 % low.
   - Getting the right answer depends on the engine-weight regression being wrong.
5. **Reserves dominate, and they are not in the error budget.**
   - Reserves are 18.9 t, 20 % of fuel: 7.6 t contingency, 3.8 t for the 200 nmi alternate and **7.5 t for the hold**. The hold burns 15 t/h, with L/D 6.2 at M0.35 / 1,500 ft and no vortex lift.
   - Removing the hold and diversion alone raises range to 4,202 nmi.
   - The reserve definition behind the 3,550 nmi figure is unknown (`VERIFICATION.md`). This assumption is worth about ±700 nmi and is not sampled.
6. **The gates are the same data point** (item 3 above; the repo acknowledges this in D-014). In effect, the case contributes a single scalar comparison.

## Statements that overstate what was shown (item 5)

- `ssbj/README.md:56`: claims an independent verification and points to a file that does not exist (defect 4).
- `docs/known_limits.md` and the run report: "`mission.integration` 1 %: Step-halving check on the integration; reported per case" is neither implemented nor applied (defect 2).
- Run report heading "Validation gates: PASS" (`model/run.py:137-138`):
  - It gives no warning that the interval excludes 41 % of samples, or that 26 of the excluded samples have valid ranges below the published value.
  - It does not mention that the nominal model needs 1,721 nmi to reach M2.
  - It does not say that published OEW or engine mass makes the reference mission infeasible.
  - It does not say the two gates are one data point (that is stated only in `reference.yaml` and D-014).
- `docs/method_notes.md`, "Every method below has a verification test":
  - The mission test (`tests/test_mission_breguet.py`) covers only the cruise integrator with a constant polar and deck.
  - The energy-method climbs, the idle descent, the reserves and `fly_distance` have no verification test.
- The run report's diagnostics table prints "- to -" for the TSFC, L/D and engine-mass intervals. The Monte Carlo propagates no error to these diagnostics, so "reported with the model's own error bar" in `reference.yaml` is not true for them.

## Concerns that are not defects

- The engine-weight method (a 1990s afterburning turbofan from Raymer App. A.4 scaled to Olympus thrust) is known to be biased low and is left uncorrected nominally. The 30 % sigma is symmetric about a value the basis says is low.
- The take-off allowance (1.5 min, zero distance, ending at M0.4 / 1,500 ft) exists only to bypass the missing low-speed aerodynamics, and it affects range (see the D-009 table).
- Contingency is 10 % of trip *fuel*, where 14 CFR 121.645 specifies 10 % of *time*; this is disclosed. The 200 nmi alternate is an assumption, also disclosed.
- 71 of 1,359 in-envelope deck points are filled by pressure-ratio scaling. Interpolation near M1.7-2.0 at 43-50 kft directly controls the near-zero-Ps climb.
- Harris wave drag is 9-11 % above OpenVSP and roughly 1.1-1.6 × the Raymer eq. 12.46 band.

## Files

- Re-run: `/tmp/verify_runs/20261004T230648-e07f5c/` (report.md, outputs.json).
- Verifier scripts: `check_physics.py`, `mc_rows.py` and `probe.py` in the session scratchpad. They are not part of the repo, and no repo code was modified.
