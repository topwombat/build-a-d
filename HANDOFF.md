# Handoff: SSBJ conceptual-design pipeline

State at hand-off: 2026-10-07, branch `claude/new-session-0808rk` (PR #1, open, not merged).
Read this first, then `CLAUDE.md` (working rules), then `ssbj/docs/brief.md` (the owner's original brief).

The repository root also holds the owner's unrelated study material (PDFs, `curriculum.md`,
`guidance.md` and so on). Leave it alone. All pipeline work lives in `ssbj/`, `tests/`, `Dockerfile`,
`pyproject.toml`, `requirements.lock` and `.github/`.

## 1. What this is

An open-tools conceptual-design pipeline for a **Mach 1.5 transatlantic supersonic business jet**. It
is proved first by reproducing Concorde blind from its mission and design definition, with an error
bar on every number.

- **Phase 1** (thin slice) is done. The owner then set an 8-item roadmap, `ssbj/reports/roadmap.md`,
  to be done **in sequence**.
- **Item 1** (supersonic-climb deficit) is **closed**.
- **Item 2** is next.

**Standing owner requirement:** each phase produces a human-readable proposal document ending in a
"Remaining deficiencies" section.
- `python -m ssbj proposal` writes it to `ssbj/reports/proposal.md`.
- `tests/test_docs.py` checks the committed copy is in sync.

## 2. Environment (as used in the previous session)

| Item | Where / how |
|---|---|
| Python | 3.11 venv at `/home/user/venv` (`/home/user/venv/bin/python`). Fresh setup: `pip install -r requirements.lock && pip install --no-deps -e .` |
| Main pins | OpenMDAO 3.45.1, numpy 2.4.6, pydantic 2.13; **pyCycle pinned to git `ee7e161`** (PyPI 4.4.0 breaks on numpy 2) |
| OpenVSP 3.49.0 | No wheel; built from source with `ssbj/docker/build_openvsp.sh` (previous build under `/home/user/ext`, rebuilt against numpy 2). OpenVSP tests skip when it is missing. |
| Container | `Dockerfile` (python:3.11.13-slim-trixie; bookworm's GCC 12 cannot compile OpenVSP 3.49). Builds in ~15 min. Optional `--secret id=extra_ca` for proxy CAs. |
| CI | `.github/workflows/ci.yml`, jobs `test` and `image` on `ubuntu-24.04`. **Has never run.** The owner is setting up self-hosted runners: wait for their labels and do not guess them. |
| Network | NASA NTRS PDFs are blocked for WebFetch but download fine with `curl` (agent proxy). |

## 3. Commands

```bash
python -m ssbj validate ssbj/validation/concorde/case.yaml
python -m ssbj run ssbj/validation/concorde/case.yaml --samples 200   # ~18 min with cached deck
python -m ssbj limits      # regenerate docs/known_limits.md (test checks sync)
python -m ssbj schema      # regenerate specs/case.schema.json (test checks sync)
python -m ssbj proposal    # regenerate reports/proposal.md (test checks sync)
python -m ssbj runs        # list the local run database (ssbj/runs/store/, git-ignored)
ruff check ssbj tests
pytest -q tests                              # unit tests, ~15-20 min (wave drag + mission)
pytest -q ssbj/validation                    # validation cases, see §5 for expected failures
```

## 4. Architecture in one screen

- `ssbj/specs/schema.py`: pydantic `Case` (mission + design).
  - A validation case is rejected if any numeric input lacks a `provenance` entry.
  - `Design.engine` is a discriminated union: `Engine` (legacy single spool, `ab_turbojet`) or
    `TwoSpoolEngine` (`two_spool_turbojet` | `mixed_flow_turbofan`).
- `ssbj/geometry/parametric.py`: in-house geometry and Mach-plane area slicing (D-004; OpenVSP is the verifier).
  - The wing inside the fuselage is excluded (D-027).
  - Optional per-station thickness profiles.
- `ssbj/disciplines/aero/`: friction, linear-theory lift, and Harris area-rule wave drag (36 roll angles × 721 stations, D-029).
  - `x_end` lets cuts end on a wind-tunnel sting.
- `ssbj/disciplines/propulsion/`:
  - `two_spool_cycle.py` (pyCycle cycle) and `two_spool.py` (problem setup, limited off-design solver, deck generation and cache, validation entry points).
  - `deck.py` is the legacy single spool.
  - `cores/` holds the cited candidate-core set: `CANDIDATES.md` and 163 sourced figures.
- `ssbj/disciplines/weights/raymer_transport.py`: Raymer eqs. 15.25-15.44 with per-component sigmas.
- `ssbj/disciplines/mission/analysis.py`: energy-method mission, cruise-climb, reserves; range and design missions.
- `ssbj/model/`:
  - `assembly.py`: OpenMDAO wiring. It dispatches on engine type (D-028).
  - `uncertainty.py`: Monte Carlo over the declared factors.
  - `run.py`: runner and report.
- Every discipline returns a `DisciplineResult` (outputs, method, `UNCERTAINTIES`, `LIMITS`, warnings).
- Caches, all committed and keyed by source hash, so changing the hashed code regenerates them:
  - `propulsion/decks/deck2s_*.json`: the **two-spool Concorde deck took 81 min**;
  - `aero/wave_cache/`.

## 5. Current results and test state

- **Concorde run** `20261009T024707-d83dc1` (propulsion sigmas 15 %, D-033): acceptance test **passes** (3 passed).
  - Range 3,644 nmi vs 3,550 published (95 % interval 2,252-6,138; 12 of 200 samples cannot fly the profile).
  - L/D 7.19 vs 7.14-7.5; TSFC 1.20 vs 1.195; 24 % of trip fuel used before cruise vs 20 %.
  - Engine mass is 44 % low and the engine over-predicts cruise thrust, so the agreement is partly offsetting errors.
  - Snapshot: `ssbj/reports/runs/concorde_20261009T024707-d83dc1.json`; report: `reports/concorde_run_20261009T024707.md`.
- **Expected red tests.** These are honest validation failures. Do not skip, loosen or tune them away:
  - `ssbj/validation/test_olympus593.py`: **3 fail** (cruise thrust +23 %, airflow at 55 kft +43 %, SLS airflow +37 %); TSFC passes.
  - `ssbj/validation/test_stca_engine.py`: **2 fail** (SFC −17 %, BPR +61 %); T3, NPR and corrected flow pass.
  - So CI will be red once it runs. The owner chose to keep failing gates as gates (Phase 1 decision 1).
- **Passing:**
  - TM X-372 wave drag (model 16-29 % above the wind-tunnel data, tolerance 50 %);
  - OpenVSP code-to-code (−6 % to 0 %);
  - all `tests/` (last full pass at `b215927`/`b84f771`, run in parts).
- **Summary of every check:** `ssbj/reports/validation_status.yaml`. Update it whenever a validation
  result changes, then regenerate the proposal.

## 6. Open owner decisions (do not decide them yourself)

They are listed in `ssbj/reports/open_items.yaml` and shown in the proposal:
1. Meaning of the STCA "extraction ratio": assumed Pt_bypass/Pt_core (D-030).
2. **Core selection.** CFM56/F101 core is the best fit but US export-controlled; PW800 is second; RR Pearl is the European option but runs hot. Supplier dialogue is needed.
3. Concorde reserve definition (D-021: IFR 14 CFR 91.167, alternate + 45 min; an assumption).
4. CI runner labels: waiting on the owner.

Already decided by the owner:
- Keep the failing test as the CI gate.
- D-004 (in-house geometry) is good for now.
- D-005 (blind = mission + design definition) is good.
- IFR reserves.
- Range is the only Concorde gate (D-023).
- Propulsion thrust and SFC sigmas widened to 15 % (D-033); validation-test tolerances stay at 10 %.
- Engine = bought hot section (core) plus our own LP system, chosen from the candidate set (D-024).
- Do the roadmap in sequence.

## 7. Next work (roadmap item 2, then 3-8)

**Item 2: validation near Mach 1.5, gated at component level.**
- Candidate cases are NASA N+2 / STCA airframe data, Aerion AS2 and F-16XL. AS2 sources are partly
  gathered in `validation/aerion_as2/`; the figures conflict widely, see the phase 1 report.
- Add gates on L/D, SFC, OEW, segment fuel fractions and **interval width**.
- Commit tolerances before running, as was done for the Olympus, TM X-372 and STCA cases.

**Engine model.** Pending model work that the validation points to (each needs a decision-log entry and a priori justification):
- duct and mixer pressure losses;
- customer bleed and power offtake;
- the off-design flow lapse that drives the Olympus airflow error;
- the 133 neighbour-filled deck points.

**Items 3-8** are in `ssbj/reports/roadmap.md`:
- 3: calibration on non-test aircraft.
- 4: field length, noise, engine requirement, trim and boom.
- 5: design loop, Aviary and optimiser.
- 6: higher-fidelity rungs.
- 7: credibility (human reviewer, source library, traceability, drawings, cost).
- 8: infrastructure.

## 8. Gotchas from the previous session

- **Deck generation is slow** (81 min on 4 cores). Any edit to the hashed propulsion functions
  (`two_spool_cycle.py`, `new_problem`, `_Solver`, `_row`, `ram_recovery`, `in_envelope`, or the grids)
  invalidates the cache. Edits to `LIMITS` or docstrings elsewhere in `two_spool.py` do not.
- pyCycle writes `*_out/` directories into the working directory. They are git-ignored; delete them freely.
- `pgrep -f <name>` inside a `bash -c` wait loop matches the loop itself. Wait on a PID or an output file instead.
- **Do not `git stash` while background jobs run.** Spawned worker processes re-import modules from disk.
- pyCycle needs a full output-vector restore after a failed solve. Set inputs after the restore,
  because auto-IVC values live in the vector. `_Solver.solve` already does this.
- The off-design continuity guard rejects corrected-speed jumps > 0.08 (solution-branch flips).
- A validation function must **raise** when its point does not converge. Never report the last
  converged state: D-025 records a void result caused by exactly that.
- Subagents in the previous session could not write files. Have them return text and save it yourself.
- Docker: `dockerd` may need starting by hand; apt needs HTTPS sources behind the proxy.

## 9. Key documents

| File | Purpose |
|---|---|
| `ssbj/docs/brief.md` | Owner's original brief (honesty rules, deliverables) |
| `ssbj/reports/decision_log.md` | D-001 … D-033: every decision with rejected alternatives |
| `ssbj/reports/roadmap.md` | The 8 roadmap items |
| `ssbj/reports/proposal.md` | Generated proposal with "Remaining deficiencies" |
| `ssbj/reports/phase1_report.md` | Phase 1 report to the owner plus updates |
| `ssbj/reports/verification_concorde_phase1.md` | Independent verifier's audit (no self-grading) |
| `ssbj/docs/known_limits.md` | Generated known-limits register |
| `ssbj/docs/method_notes.md` | Methods, equations, verification status |
| `ssbj/validation/*/SUMMARY.md` | Per-case results and sensitivities |
