# Working rules for agents on this repository

Pipeline code is in `ssbj/` and `tests/`; the rest of the root is the owner's study material (do not
touch). Start with `HANDOFF.md`; the owner's brief is `ssbj/docs/brief.md`.

## Honesty rules (from the brief; enforced by review, not just tooling)

1. **Provenance on every number.** Validation-case inputs need a `provenance` entry (the schema
   rejects the case otherwise). Mark assumptions `ASSUMPTION:` in the provenance text.
2. **Error bar on every number.** New disciplines declare `UNCERTAINTIES` (1-sigma, with a basis) and `LIMITS`.
3. **Cite reference data; never fill from memory.** Record source, URL, page, exact quote and
   `source_quality` (pdf_read / page_read / search_snippet). Say so when a source is unreachable.
4. **Blind reproduction; no tuning on test aircraft.** Fix tolerances and sigmas in a commit
   *before* running the model against the reference data. Sensitivity studies are reported, never adopted
   to close a gap.
5. **Tests are the gate.** Never skip, xfail, loosen or delete a failing validation test. Currently
   `test_olympus593.py` (3) and `test_stca_engine.py` (2) fail on purpose; see `HANDOFF.md` §5.
6. **No agent grades its own work.** Validation sign-off needs an independent verifier or a human.
7. **Known limits register.** Add limits to the module's `LIMITS`; run `python -m ssbj limits`.
8. **Decisions logged.** Every non-trivial choice goes in `ssbj/reports/decision_log.md` (next: D-033),
   with the alternatives rejected and whether it was made before or after seeing results.
9. **New solvers earn trust** with a verification test against a closed form or independent code.

Owner decisions are the owner's: list open ones in `ssbj/reports/open_items.yaml`, don't decide them.

## Every phase / result change

- Update `ssbj/reports/validation_status.yaml`. When a Concorde run is the new reference, snapshot its
  `outputs.json` into `ssbj/reports/runs/`.
- Regenerate: `python -m ssbj limits`, `python -m ssbj schema`, `python -m ssbj proposal`.
- `ruff check ssbj tests` and the relevant `pytest` before pushing.

## Git

- Branch `claude/new-session-0808rk` (PR #1). Push with `git push -u origin <branch>`. Don't open PRs unasked.
- Commit the regenerated caches (`propulsion/decks/`, `aero/wave_cache/`) when their keys change, and
  remove stale ones.
- No model identifiers in commits or PRs.
