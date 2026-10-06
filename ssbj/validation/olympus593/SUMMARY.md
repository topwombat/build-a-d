# Olympus 593 Mk 610: independent validation points (2026-10-06)

The cited entries with verbatim quotes are in `sources.yaml` (38 entries). The research agent's summary
was saved by the main session because the agent could not write report files.

## Usable points

| # | Quantity | Value | Conditions | Source (quality) |
|---|---|---|---|---|
| 1 | Net thrust per engine | **10,030 lbf** | M2.00, 53,000 ft cruise | NASA TM-4144 (Morris et al. 1989) Table II p.9 (pdf_read) |
| 2 | Cruise TSFC | **1.19 /h** (41 % overall efficiency) | M2 cruise | TM-4144 p.2 (pdf_read); conflicts 1.195 (Wikipedia, citation needed), 1.165 (Mair & Birdsall via Starr, tertiary) |
| 3 | Engine airflow, cruise | ~210 lb/s per engine (implied) | M2.0, 55,000 ft | Berger, AGARD CP-242 / NASA TM-75238 p.20-5 (pdf_read) |
| 4 | Engine airflow, SLS | 410 lb/s | SLS | TM-4144 p.2 (pdf_read) |
| 5 | Intake pressure recovery | **0.937** | M2, 53,000 ft | TM-4144 Fig. 2 p.12 (pdf_read); 7.3:1 intake ratio (≈0.933) via Wikipedia/Cumpsty supports it; ≈0.96 at critical with 6 % bleed (Slater, secondary) conflicts |
| 6 | Engine compressor PR at cruise | 12.07 (overall 88.5) | M2, 53,000 ft | TM-4144; conflicts 11.3 (Cumpsty), ~14 (Berger) |
| 7 | Component losses at cruise | compressor ηpoly 0.90; burner ΔP 9 %; turbine ηad 0.885 HP / 0.851 LP; cooling 2.2 % / 11.3 %; exhaust ΔP 2 % | M2, 53,000 ft | TM-4144 Fig. 2 (NASA estimate) |
| 8 | Cruise procedure | cruise-climb at M2.0, max continuous; N. Atlantic 50→57 kft | best range | McKinlay, Heaton & Franchi, ICAS 1976 pp.566, 569-570 (primary) |
| 9 | Transonic schedule | reheat from M0.95 (Vmo climb), off at M1.7 | | ICAS 1976 p.566 |
| 10 | Reheat boost | +20 % | take-off, M0.95-1.7 | Wikipedia citing Hooker; spec ratio 1.21 agrees |
| 11 | SLS reheat thrust | 37,700 / 38,900 lbf (TM-4144 contradicts itself); 38,050 (Wikipedia) | SLS | |
| 12 | Thrust lapse | cruise/SLS-dry ≈ 0.31-0.32 | derived from 1, 11 | |
| 13 | Shape checks | TSFC +6 % from M1 to M2 above 40 kft; at 39 kft dry thrust exceeds drag only above M1.2 | | Starr summarising Mair & Birdsall (tertiary) |
| 15 | Friction share of cruise drag | about one-third | supersonic cruise | ONERA, NTRS 19840010085 |

Generic Mach 1.4 mixed-flow turbofan (NASA NPSS: CFM56-7B core, new fan, forced mixer), Berton, Huff &
Seidel AIAA 2020-0263: at M1.4 / 50 kft, Fn 3,330 lb, SFC 0.943, BPR 2.9, **T3 1450 °R**, OPR 22; above
10,000 ft thrust is "limited by hot section temperatures". Slater AIAA 2020-2090: 2D inlet recovery
0.970-0.973 at M1.4, 0.966 at M1.7, 0.935 at M2.0.

## First comparison with the current deck (commit d93c6fa)

| Point | Published | Deck | Difference |
|---|---|---|---|
| Dry thrust per engine, M2.0 / 53,000 ft | 10,030 lbf | 9,170 lbf | −8.6 % |
| TSFC, same point | 1.19 /h | 1.12 /h | −6 % |
| Intake recovery at M2 | 0.937 | 0.925 (MIL-E-5008B) | −1.3 % |

The deck is low on thrust and low on fuel consumption: the offsetting errors seen at aircraft level
start inside the engine model.

## Gaps

- Spool speeds at any condition.
- A quoted cruise fuel flow (only derived: ≈11,900 lb/h per engine).
- Nozzle coefficients.
- Thrust and SFC tables versus Mach and altitude, especially transonic M1.0-1.7.
- Take-off lapse and reheat SFC.
- Any Concorde drag polar.
- Primary sources not reached: Rettie & Lewis 1968, Leyman 1986, Mair & Birdsall (1992), Hooker,
  Cumpsty, SAE 760888, Flight 1969/71.
- Blocked hosts: heritageconcorde.com, pprune.org, concordesst.com, archive.org.

## Two-spool result (commit after D-026; engine sized at cruise, limited max power)

| Check (tolerance 10 %, committed in advance) | Published | Model | Result |
|---|---|---|---|
| Cruise thrust, M2.0 / 53 kft | 10,030 lbf | 12,333 lbf (+23 %) | FAIL |
| Cruise TSFC | 1.19 /h | within 10 % | pass |
| Cruise airflow, M2.0 / 55 kft | ~210 lb/s | 301 lb/s (+43 %) | FAIL |
| SLS airflow | 186 kg/s | 255 kg/s (+37 %) | FAIL |

The model's specific thrust is 15-27 % low across the envelope (cruise 402 vs 468 N s/kg; SLS 548 vs
750), so it needs too much airflow, which inflates cruise thrust. Not tuned; see the sensitivity
study and decision log.

## Sensitivity of the two-spool result (for the owner; nothing adopted)

One assumption changed at a time from the committed case (cruise thrust at M2.0 / 53 kft; published 10,030 lbf, TSFC 1.19; airflow at M2.0 / 55 kft ~210 lb/s; SLS airflow 186 kg/s):

| Variant | Cruise Fn, lbf | TSFC | W at 55 kft, lb/s | SLS W, kg/s |
|---|---|---|---|---|
| A baseline | 12,333 | 1.200 | 301 | 255 |
| B no LPT cooling | did not converge | | | |
| C HPT/LPT cooling swapped | 11,805 | 1.143 | 275 | 233 |
| D burner dP 5 % (was 9 %) | 12,193 | 1.181 | 292 | 247 |
| E LP/HP PR split 2.5 / 4.83 | 12,491 | 1.197 | 304 | 255 |
| F nozzle Cv 0.995 | 12,634 | 1.154 | 296 | 251 |
| G LP/HP PR split 4.8 / 2.51 | 12,268 | 1.207 | 301 | 256 |
| H T4 1,980 °F (text value) | 12,356 | 1.199 | 297 | 252 |

No single plausible assumption moves airflow by more than 9 %: the 37-43 % airflow excess (specific thrust 15-27 % low) is structural, not an input choice. Candidates: the generic maps' off-design flow lapse between the M2 design point and SLS, and the absent variable-geometry intake schedule.
