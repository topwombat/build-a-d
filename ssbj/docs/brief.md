# SSBJ Design Pipeline: Handoff Brief

Oct 4, 2026 · @Alex Zuzin

Build the thin slice of an agentic conceptual-design pipeline for a Mach 1.5 transatlantic business jet, and prove it by reproducing Concorde from its mission spec. You are the setup agent: this brief is self-contained, and everything in it can be changed by the owner.

## Defaults to confirm

Three calls were open when this brief was written. Each has a default so work can start; the owner may overrule any of them.

| Decision | Default taken | Why | Cost of changing later |
| --- | --- | --- | --- |
| Toolchain posture | Open and unrestricted tools only, from day one | The operating company is European; US export-restricted codes (Cart3D, FUN3D, sBOOM) cannot be used there | Low to add restricted tools later in a US-only fork; high to remove them once results depend on them |
| Engine in version one | Parametric engine deck with three or four cycle variables exposed to the optimizer | The engine is co-designed with the airframe, and the engine requirement is a primary output | Moderate: a fixed deck is simpler but hides the main trade |
| Compute budget | Phase 1 runs on a single multi-core machine; no CFD until Phase 4 | Low-rung methods cost seconds per candidate | None: budget is set per phase |

If a default looks wrong once you are in the work, stop and ask the owner; do not quietly switch.

## Reference mission and first milestone

Phase 1 is done when the pipeline, given only Concorde's mission spec, predicts its range and fuel burn with a stated error bar that contains the real values.

**Target aircraft (the eventual design case).** Only the first two rows are fixed by the owner; the rest are placeholders to be confirmed.

| Parameter | Value | Status |
| --- | --- | --- |
| Cruise Mach | 1.5 | Fixed |
| Route network | Transatlantic, supersonic over water only | Fixed |
| Design range | 4,000 nmi with reserves | Placeholder |
| Cabin | 8 to 12 passengers | Placeholder |
| Field length | 7,000 ft or less | Placeholder |
| Sonic boom | Reported, not constrained | Fixed |
| Takeoff noise | Current subsonic certification limits | Placeholder |

**Validation cases, in order.**

1. Concorde: the only richly documented civil supersonic aircraft. Gather geometry, weights, engine data and mission performance from published sources, and cite every number.
2. A published Mach 1.4 to 1.6 business jet study (Aerion AS2 is the obvious one): check that sizing lands near the published figures.
3. One or two further slender-wing cases from NASA supersonic transport studies or public drag prediction workshops, added as data allows.

The validation set will be three or four cases, not twenty. Say so in every report.

## Phase 1 thin slice

Build one end-to-end path from mission spec to range prediction before deepening any single module.

- [ ] **Repository and environment.** One repository, a container image with pinned versions, and continuous integration that runs the test suite on every change.
- [ ] **Run database.** Every case stores inputs, code version, outputs, error estimate and wall time. SQLite plus files on disk is enough.
- [ ] **Mission spec schema.** A typed, validated file format (YAML or TOML with a schema) covering payload, range, Mach, altitudes, reserves, field length and the full profile including subsonic legs and transonic acceleration.
- [ ] **Parametric geometry.** An OpenVSP model driven from a parameter vector, covering wing planform and thickness, fuselage area distribution, tail and nacelles. Detect and report geometry failures.
- [ ] **Low-rung aerodynamics.** Skin friction, area-rule wave drag, and linear-theory drag due to lift, producing a drag polar across the Mach range.
- [ ] **Engine deck.** A pyCycle model of a low-bypass turbofan or turbojet giving thrust and fuel flow against Mach and altitude, with inlet and nozzle loss models and a weight and size estimate.
- [ ] **Statistical weights.** Component weight build-up with an explicit uncertainty on each component.
- [ ] **Mission analysis.** Segment-by-segment integration of the profile, returning fuel burn, range and the transonic thrust margin.
- [ ] **OpenMDAO wiring.** All modules joined in one model, runnable from a single command with a mission spec file.
- [ ] **Concorde case.** Its spec and published data in the repository as an automated test, with the comparison written to a short report.

**Suggested layout**

```
ssbj/
  specs/         mission spec files and schema
  geometry/      parametric model and meshing
  disciplines/   aero, propulsion, weights, mission, one folder each
  model/         OpenMDAO assembly and optimizers
  validation/    reference aircraft data with sources, and tests
  runs/          run database and outputs
  reports/       decision log and generated reports
  docs/          known limits register, method notes
```

## Modules

Every discipline has the same interface: inputs, outputs, an error estimate, and a list of conditions under which it should not be trusted. Only the first four rows are in Phase 1.

| Discipline | Low rung | High rung | Starting tool | Phase |
| --- | --- | --- | --- | --- |
| Aerodynamics | Skin friction, area-rule wave drag, linear-theory lift drag | Euler for cruise; RANS for low speed and transonic | OpenVSP tools, then SU2 | 1, then 4 |
| Propulsion | Parametric cycle deck with inlet and nozzle losses | Installed inlet and nozzle CFD | pyCycle | 1, then 4 |
| Weights and structures | Statistical component weights | Beam and shell sizing under load cases | Own code, then OpenAeroStruct or TACS | 1, then 4 |
| Mission performance | Segment-by-segment fuel burn | Trajectory optimization | Own code or NASA Aviary | 1 |
| Stability and trim | Center-of-gravity envelope, lift-center shift, trim drag | Control power at rotation | Own code | 4 |
| Field and low speed | Takeoff and landing distance, approach speed | High-lift CFD | Own code, then SU2 | 4 |
| Noise | Jet-velocity takeoff noise estimate | Certification-point prediction | Own code | 4 |
| Aeroelastic | Static deflection | Flutter screening | OpenAeroStruct | 4 |
| Economics | Development, unit and operating cost | Fleet-level model | Own code | 5 |

The three that dominate this aircraft class are weights, propulsion integration and the low-speed end. Expect weights to carry the widest error bar.

## Honesty rules

These apply from the first commit; they are the product, not an add-on.

1. **Every number has provenance.** A result records the method, code version and inputs that produced it.
2. **Every number has an error bar.** A module that cannot estimate its error states a conservative one and says why.
3. **Reference data is cited.** No validation figure enters the repository without a source link or citation. Do not fill gaps from memory.
4. **Blind reproduction.** Validation cases are run from the mission spec alone. Do not tune a module against the aircraft it is tested on; any calibration uses separate data and is recorded.
5. **Tests are the gate.** Acceptance is a passing test, never an agent's opinion that a result looks right.
6. **No agent grades its own work.** A verifier that did not write or run a case checks it.
7. **Known limits are written down.** Each module keeps a register of where it is weak, and error bars widen outside its validated range.
8. **Decisions are logged as they happen.** Each pruning step records what was dropped and why, so reports are generated from the log.
9. **New solvers earn trust.** Any code we write or modify passes method verification and public benchmark cases before its output is used.

## Later phases

Do not start these in the setup session; they are here so Phase 1 interfaces are designed with them in mind.

1. **Phase 2, honesty layer.** Uncertainty propagation through the whole model, the known-limits register, and the remaining validation cases as automated tests.
2. **Phase 3, search.** Optimizers, surrogate models, promotion rules between fidelity rungs, and the decision log.
3. **Phase 4, fidelity.** Add higher rungs one discipline at a time, starting with whichever has the widest error bar. This includes an in-house Cartesian Euler solver with adjoint mesh adaptation if open tools prove too slow in the loop.
4. **Phase 5, outputs.** Report generator that writes plain English from the decision log, renders from the analysis geometry, standard charts, the engine requirement spec, and the cost model.
5. **Phase 6, engine co-design.** One core sized against both the jet and an uncrewed aircraft mission, showing what commonality costs each.

## Verify at setup

Nothing below was checked when this brief was written; tool names and claims come from general knowledge.

- [ ] Current version, licence and maintenance status of OpenVSP, OpenMDAO, pyCycle, SU2, OpenAeroStruct, TACS and Aviary.
- [ ] That each tool installs and runs headless in the container, and that their versions are mutually compatible.
- [ ] Export-control status of every tool and dataset used, confirmed by the owner's counsel before the European side relies on it. The statement that Cart3D, FUN3D and sBOOM are restricted to US persons should be confirmed too.
- [ ] Whether OpenVSP's wave drag tool is accurate enough at Mach 1.5 or needs replacing.
- [ ] Which Concorde and AS2 figures are available from citable public sources, and which are missing.

**Report back at the end of the session:** what was built, what passes, the Concorde comparison with error bars, and anything in this brief that turned out to be wrong.
