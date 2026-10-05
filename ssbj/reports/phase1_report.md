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
