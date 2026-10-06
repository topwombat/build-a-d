# STCA turbofan validation: result

Test `ssbj/validation/test_stca_engine.py` (tolerance 10 %, committed before the run at `456e33c`).
Design point M1.4 / 50,000 ft ISA, per engine. Targets are NASA NPSS model results (AIAA 2020-0263 Table 1;
corrected flow from AIAA 2020-2090), so this is model-to-model.

| Check | NASA | ssbj | Result |
|---|---|---|---|
| Net thrust (input) | 3,330 lbf | 3,330 lbf | input |
| SFC | 0.943 /h | 0.778 /h (−17 %) | **FAIL** |
| Bypass ratio | 2.9 | 4.67 (+61 %) | **FAIL** |
| Compressor exit temperature | 1,450 °R | 1,417 °R (−2.3 %) | pass |
| Nozzle pressure ratio | 5.9 | 6.02 (+2.1 %) | pass |
| Engine-face corrected flow | 413 lbm/s | 416 lbm/s (+0.6 %) | pass |

## Sensitivity (for the owner; nothing below is adopted)

| Variant | SFC | BPR | T3 °R | NPR | Wc2 |
|---|---|---|---|---|---|
| As committed (ER read as Pt_bypass/Pt_core = 1.1) | 0.778 | 4.67 | 1417 | 6.02 | 415.7 |
| ER read the other way (Pt_core/Pt_bypass = 1.1) | 0.797 | 3.98 | 1417 | 6.32 | 374.3 |
| ER = 1.0 | 0.786 | 4.33 | 1417 | 6.17 | 395.1 |
| No turbine cooling | 0.759 | 5.65 | 1417 | 6.04 | 427.8 |
| HPT cooling 10 % | 0.782 | 4.31 | 1417 | 6.01 | 413.8 |

## Reading

- The model's core delivers more work per unit core flow than NASA's model. At fixed fan PR and mixer pressure balance, the extra LP-turbine work goes into bypass flow: BPR is too high, and SFC is too low because less fuel is burned per unit of thrust.
- None of the plausible single changes closes the gap. The extraction-ratio reading moves BPR by 0.7, cooling by 1.0.
- Likely missing items, none modelled yet:
  - duct and mixer pressure losses (the cycle has none between components);
  - customer bleed and power offtake;
  - CFM56 core characteristics (NASA held the donor engine's HPC/HPT maps, bleeds and areas; ssbj uses generic maps and efficiencies).
- Opposite sign to the Olympus result (specific thrust 15–27 % low there), so it is not a single systematic bias.
- Specific thrust and T3 match: the airflow and the compressor are right. The error is in the work split and losses.

Not tuned. A calibration step (roadmap item 3) must use engines other than the test cases.
