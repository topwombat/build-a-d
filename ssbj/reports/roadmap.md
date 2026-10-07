# Roadmap to a proposal (owner direction 2026-10-06)

Done in sequence. Each step ends with tests, a decision-log entry and a regenerated proposal.

**Standing requirement (owner):** every phase produces a human-readable proposal document,
generated from the pipeline: the aircraft as currently designed, its performance with error
bars, the engine requirement, and a final section **"Remaining deficiencies"**. That section
draws from the known-limits register, open validation failures and open owner decisions.

1. **Supersonic-climb deficit.** Validate the engine deck and the area-rule wave drag separately
   against independent data (Olympus 593 at M2 / 55,000 ft; a public NASA arrow-wing wind-tunnel
   case). Upgrade the engine to a two-spool cycle with scheduled-intake recovery and spool-speed
   limits. No tuning to Concorde.
2. **Validation near Mach 1.5, gated at component level.** NASA N+2 supersonic business-jet
   studies, X-59, F-16XL, Aerion AS2 (AIAA papers). Gates on L/D, SFC, OEW, segment fuel
   fractions and interval width.
3. **Calibration on non-test aircraft, then blind tests.** Bayesian fit of class factors; correlated
   uncertainty; global sensitivity analysis.
4. **Design-deciding constraints.** Field length and Chapter 14 noise (vortex lift, high lift,
   jet noise), engine requirement as an output, trim and CG travel, sonic boom.
5. **Design loop.** MTOW closure, constraint diagram, trajectory optimisation (Aviary),
   optimiser with derivatives or surrogates, faster deck and mission.
6. **Higher-fidelity rungs where sensitivity justifies them.** VSPAERO, then SU2 Euler, with
   promotion rules.
7. **Proposal credibility.** Human reviewer per validation case, hash-pinned source library,
   requirements traceability, generated drawings, weight statement, payload-range, cost.
8. **Infrastructure.** Self-hosted CI with caches (owner in progress), content-hash cache keys,
   queryable run database.

**Engine architecture (owner direction, to be logged as D-024 when item 1 starts):** the hot
section is bought from an engine supplier; the rest of the engine (inlet, fan/LP compression,
LP turbine, mixer, nozzle, installation) is our design.
