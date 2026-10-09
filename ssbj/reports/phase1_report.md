# Phase 1 setup session: report to the owner

2026-10-04 · branch `claude/new-session-0808rk` · PR #1 · final run `20261004T233754-b4cf09` at commit `0dcfb6b`

**The validation set is three or four cases, not twenty.** One is done (Concorde), and it does not meet the milestone.

## Verdict

**The Phase 1 milestone is not met.** The pipeline runs end to end from one case file and records every run with provenance and error bars. Given Concorde's mission and design definition, its predicted range brackets the published value. It does not predict that Concorde can fly that range:

| Gate (published, page-read) | Published | Model nominal | Model 95 % interval | Result |
|---|---|---|---|---|
| Range at max fuel, 8,845 kg payload, "FAR reserves" | 3,550 nmi | 3,451 nmi (−2.8 %) | 2,640 – 5,027 nmi (157 of 200 samples flyable) | inside |
| Fuel to fly 3,550 nmi with that payload | 95,680 kg (max fuel) | not flyable | 62,142 – 94,886 kg (53 of 200 samples flyable) | **outside** |

The two gates are one published data point read two ways. The model falls 99 nmi short at full tanks and cannot close the gap with more fuel: past about 102 t, the extra weight costs more in the supersonic climb than the fuel buys. The acceptance test (`ssbj/validation/test_concorde.py`) therefore fails, which is the honest state.

## Why: the model is right on range only by accident

The independent verifier's sensitivity runs, together with the diagnostics, show offsetting errors:

| Diagnostic | Published (page-read) | Model nominal (95 % interval) |
|---|---|---|
| Cruise L/D at M2 | 7.14 – 7.5 | 6.63 (5.77 – 8.58) |
| Cruise TSFC | 1.195 /h (Wikipedia, "[citation needed]") | 1.12 (1.02 – 1.23) |
| OEW | 78,700 kg | 73,201 kg (54,251 – 92,703) |
| Engine dry mass | 3,175 kg | 1,767 kg (812 – 2,884) |
| Trip fuel burned before cruise | 20 % (ICAS 1976) | 68 % |
| Distance covered before cruise | 9 % (ICAS 1976) | 55 % |

- **Supersonic climb is far too slow.** M1.7 → 2.0 takes 97 min, 1,746 nmi and 37 t of fuel; dry excess thrust there is too small. Likely causes: the single-spool, generic-map engine deck at high Mach, and/or wave drag (the Harris code runs about 10 % above OpenVSP).
- **Low weight and low TSFC hide it.** The engine weight scaling uses a 1990s reference engine (biased low, as declared before the run). Setting engine mass, OEW or TSFC to its published value alone makes the 3,550 nmi mission infeasible (verifier).
- **The reserve definition swings range by about 700 nmi** (19 t of reserves, of which the hold is 7.5 t), and no source defines Heritage's "FAR reserves". This is outside the error budget.

None of this was tuned away. Error sigmas were committed before the first comparison (`bf5c882`). Every input change after it is logged and justified in `decision_log.md` (D-009, D-016, D-018), and each moved range *away* from the published value or was a feasibility fix.

## What was built

| Brief item | Status |
|---|---|
| Repository, container, CI | Done: `Dockerfile` (Python 3.11, Debian trixie, OpenVSP 3.49.0 built from source), `requirements.lock`, `.github/workflows/ci.yml`. CI has not run on GitHub yet. |
| Run database | Done: SQLite plus a file store; each record holds inputs, git SHA and dirty flag, outputs, error estimate, warnings and wall time; failures recorded too |
| Mission spec schema | Done: pydantic schema, JSON schema exported. A validation case is rejected if any numeric input lacks provenance |
| Parametric geometry | Done in-house, verified against OpenVSP: wing area exact, wetted areas within 1-4 %, fuselage-alone within 1 % (D-004 departs from the brief, **confirm**). Geometry failures detected and reported |
| Low-rung aero | Skin friction, Harris area-rule wave drag (Sears-Haack exact), linear-theory lift and K |
| Engine deck | pyCycle afterburning turbojet, four cycle variables, MIL-E-5008B inlet recovery, Raymer weight scaling; cached deck (bit-reproducible) |
| Statistical weights | Raymer transport eqs. 15.25-15.44 (hand-checked against the scan), per-component sigmas plus a correlated class factor |
| Mission analysis | Energy-method climb and accelerations, cruise-climb, descent, reserves; transonic thrust margin output |
| OpenMDAO wiring | Done; `python -m ssbj run <case.yaml>` |
| Concorde case | Case, cited and page-verified reference data, acceptance test, run report. **Fails the fuel gate** |

**Tests:** final full run at `0dcfb6b`+report: 50 passed, 1 failed (`test_gates_inside_error_bar`, the fuel gate, as described above). 46 tests also passed inside the built image, OpenVSP cross-checks included; the image was built before the last two mission tests were added.

## What in the brief turned out to be wrong or harder than stated

1. **OpenVSP has no pip wheel.** It must be built from source (about 10 min), and 3.49.0 does not compile with GCC 12 (Debian bookworm), so the image uses trixie.
2. **pyCycle's PyPI release (4.4.0) breaks on numpy 2.** OpenMDAO 3.40+ requires numpy 2, so pyCycle is pinned to an unreleased git commit.
3. **Concorde is less richly documented than assumed.** The type certificate data sheet and Leyman (1986) were not reachable. The headline range point does not define its reserves, and the max payload on the same source page is self-inconsistent (13,380 vs 12,700 kg). Aerion AS2 figures conflict widely: MTOW 115,000-150,000 lb across sources.
4. **The milestone test ("error bar contains the real value") is weak.** A wide interval passes trivially, and a model can pass for the wrong reasons. The run here passed before the verifier's fixes. Suggest adding component diagnostics (L/D, SFC, OEW, pre-cruise fuel share) as gates and a bound on interval width.
5. **OpenVSP's wave-drag accuracy at M1.5 is still open.** It agrees with the in-house Harris code to about 10 %, but neither has been checked against test data. Public drag-workshop data is needed (validation case 3).
6. **Weights did not dominate the error.** The largest effects were supersonic excess thrust, the reserve definition, and engine weight.
7. **Export status of Cart3D, FUN3D and sBOOM was not checked.** It still needs counsel, as the brief says.

## Decisions for the owner

- D-004 (in-house geometry, OpenVSP as verifier) and D-005 (meaning of "blind": mission plus design definition as inputs).
- Whether to keep the failing acceptance test as the CI gate (the current honest state) or record it as a known failure while Phase 2 works on the supersonic climb. Do not mark it skipped without that decision.
- The reserve definition for the Concorde point: a primary source is needed, ideally the flight manual or the TCDS.

## Next steps (proposed, not started)

1. Diagnose the supersonic-climb deficit against independent engine data: Olympus 593 thrust at M2/55,000 ft from ICAS 1976 or the Rolls-Royce literature.
2. Calibrate the engine weight against a separate engine (not Concorde's), as Raymer §15.4 suggests.
3. Obtain the TCDS and Leyman 1986; then add validation case 2.

Details: `decision_log.md`, `verification_concorde_phase1.md` (independent verifier), `concorde_run_20261004T233754.md`, `../docs/method_notes.md`, `../docs/known_limits.md`, `../validation/concorde/VERIFICATION.md`.

## Update 2026-10-05: IFR reserves (owner decision D-021)

Reserves changed per owner to 14 CFR 91.167(a): alternate (200 nmi assumed) plus 45 min, no contingency. The change was made after results were known and moves range toward the published value. The search bug it exposed is fixed in D-022. Run `20261005T001915-000e00` at `1438c4c`:

| Gate | Published | Model nominal | Model 95 % interval | Result |
|---|---|---|---|---|
| Range at max fuel, 8,845 kg | 3,550 nmi | 4,011 nmi (+13 %) | 3,079 – 5,804 (157/200 flyable) | inside |
| Fuel to fly 3,550 nmi | 95,680 kg | 83,395 kg (−13 %) | 57,105 – 93,336 (147/200) | outside |

**The fuel gate's "outside" is partly a statistical artifact.** The published fuel is the tank capacity, and the search is capped there (D-022). Samples that need more than the tanks are therefore censored as infeasible (33 of 200) instead of entering the interval. Counting them as "needs more than 95,680 kg", 33 of 180 samples that can fly at all lie above the published value, so it would sit inside a censoring-aware 95 % interval. I have not changed the gate evaluation: that would be changing the test after seeing the result. The owner should decide (see below).

Diagnostics are unchanged in substance: L/D 6.61, 61 % of trip fuel and 48 % of distance before cruise (published 20 % and 9 %). The supersonic-climb deficit remains the main model error. The range now overshoots by 13 % instead of undershooting; that swing shows how much the unconfirmed reserve definition moves the answer.

**Decision needed:** (a) drop the fuel gate as redundant (it is the range gate inverted); (b) evaluate it with censoring at tank capacity; or (c) keep it as is (fails).

## Update 2026-10-05: single range gate (owner decision D-023)

The fuel-for-range check is now a diagnostic. The acceptance test (`ssbj/validation/test_concorde.py`) **passes** at commit `2a2ec1f`: 3 passed. The range gate passes with range at 4,011 nmi nominal against the published 3,550 nmi (95 % interval 3,079-5,804).

This pass depends on two owner decisions made after results were known: the IFR reserve definition (D-021) and the single gate (D-023). It is not blind with respect to either. The model errors behind it are unchanged: L/D low, engine weight low, and a supersonic climb about 3x too long. The pass shows the pipeline works end to end with honest error bars. It does not show the low-rung models are accurate for this class.


## Update 2026-10-06: roadmap item 1 (supersonic-climb deficit)

Run `20261006T191624-74a9a6` (two-spool engine, corrected wave drag). The acceptance test passes (3 passed).

| Quantity | Published | Before (single spool, 20261005) | Now |
|---|---|---|---|
| Range at max fuel | 3,550 nmi | 4,011 | 3,644 (95 %: 2,457-4,964) |
| Cruise L/D | 7.14-7.5 | 6.61 | 7.19 |
| Cruise TSFC | 1.195 /h | 1.12 | 1.20 |
| Trip fuel before cruise | 20 % | 61 % | 24 % |
| Distance before cruise | 9 % | 48 % | 6.7 % |
| Engine dry mass | 3,175 kg | 1,767 | 1,767 |

What changed:
- **Wave drag.** Two code defects were found by the TM X-372 wind-tunnel check: the wing inside the fuselage was counted twice, and the sting closure added a spurious base drag. Concorde wave drag fell 8-10 %, and the OpenVSP gap closed.
- **Engine.** The engine is now a two-spool turbojet designed at M2 cruise, with spool-speed limits.

What did not change:
- The engine model still fails its own validation: Olympus cruise thrust +23 % and airflow +43 %; the STCA turbofan SFC is 17 % low.
- Engine weight is still 44 % low.

Part of the improved climb therefore comes from excess thrust. The human-readable proposal with "Remaining deficiencies" is `proposal.md`.

## Update 2026-10-09: propulsion sigmas widened to 15 % (owner decision D-033)

Run `20261009T024707-d83dc1`. The nominal values are unchanged: range 3,644 nmi.
- **95 % range interval:** 2,457-4,964 nmi before, now 2,252-6,138 nmi. The gate still passes.
- **Cruise TSFC 95 % interval:** 1.10-1.34 /h before, now 0.88-1.59 /h.
- **Samples that cannot fly the range mission:** 1 of 200 before, now 12 of 200 (10 of them in the subsonic climb).

The engine validation tests keep their 10 % tolerances and still fail.
