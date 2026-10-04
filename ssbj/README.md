# SSBJ conceptual-design pipeline: Phase 1 thin slice

One end-to-end path from a mission spec file to a range and fuel-burn prediction with error
bars, for a Mach 1.5 transatlantic business jet. It is proved first on Concorde.

**The validation set is three or four cases, not twenty.** One case is done so far (Concorde).

## Run it

```bash
pip install -r requirements.lock && pip install --no-deps -e .
python -m ssbj validate ssbj/validation/concorde/case.yaml   # schema + geometry checks
python -m ssbj run ssbj/validation/concorde/case.yaml        # nominal + 200-sample Monte Carlo
python -m ssbj runs                                           # list the run database
pytest -q                                                     # unit tests + Concorde acceptance test
```

Or use the pinned image: `docker build -t ssbj . && docker run --rm ssbj`. The image builds
OpenVSP 3.49.0 headless from source, which takes about 15 minutes. See the `Dockerfile`
header for proxy and CA options.

## Layout

```
ssbj/
  specs/         case schema (pydantic) and exported JSON schema
  geometry/      parametric analysis geometry, failure checks, OpenVSP model for cross-checks
  disciplines/   aero/ propulsion/ weights/ mission/ (one folder each, common interface)
  model/         OpenMDAO assembly, Monte Carlo error bars, case runner and report
  validation/    reference aircraft: case files, cited reference data, acceptance tests
  runs/          SQLite run database (store/ is git-ignored)
  reports/       decision log and generated reports
  docs/          known-limits register (generated), method notes, tool check
```

## Interface every discipline follows

Each discipline returns a `DisciplineResult` (`ssbj/core/interface.py`) containing:
- outputs;
- a method string;
- error estimates, as independent multiplicative factors with a 1-sigma value and a stated basis;
- the conditions under which it should not be trusted, plus any that were triggered on this run.

The Monte Carlo samples every declared factor. Each run stores its inputs, code version
(git SHA plus a dirty flag), outputs, error estimate, warnings and wall time.

## Honesty rules: where each is enforced

| Rule | Mechanism |
|---|---|
| Provenance | Run database row per case; `code_version()`; report header |
| Error bars | Every discipline declares sigmas; Monte Carlo in every run |
| Cited reference data | `Case` rejects a validation case with any numeric input lacking a provenance entry; `reference.yaml` cites every gate value |
| Blind reproduction | Inputs are mission plus design definition only (D-005); sigmas committed before the first comparison (D-008) |
| Tests are the gate | `ssbj/validation/test_concorde.py` |
| No self-grading | A separate verifier agent (not the one that wrote or ran the case) re-ran and audited it: `reports/verification_concorde_phase1.md`. Its findings were fixed in D-017 to D-019. It is still a model checking a model's work, not a human review. |
| Known limits | `docs/known_limits.md` is generated from the code and checked in CI |
| Decisions logged | `reports/decision_log.md` |
| New solvers earn trust | Sears-Haack, Breguet, step-halving, fuel-for-distance round trip, pyCycle atmosphere and OpenVSP cross-check tests. The climb, descent and reserve segments have no independent verification case yet. |
