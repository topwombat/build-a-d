# Candidate gas-generator cores for a Mach 1.4-1.6 SSBJ

The idea is to buy the hot section (HP compressor, combustor and HP turbine) and design the fan, LP spool, mixer, nozzle and intake in-house.

- Every figure below has an entry in `candidates_sources.yaml` (163 entries), with the exact quote, URL and section. All figures were retrieved on 2026-10-06.
- Source types:
  - EASA type-certificate data sheets (TCDS), read as PDFs.
  - Manufacturer pages: GE Aerospace, Rolls-Royce, MTU, Honeywell.
  - Trade press: Aviation Week leads, AIN, FlightGlobal standfirsts, Leeham News.
  - Wikipedia, read as wikitext. These entries are secondary, and the YAML says so.
- Tags used in this file:
  - **[inferred]** marks something I worked out from the sources. No source states it.
  - **[judgement]** marks my own assessment.
- Pages I could not read: Safran (Cloudflare 403), pwc.ca and prattwhitney.com (403), cfmaeroengines.com (429), web.archive.org (connection reset) and NASA NTRS API (403). As a result, Safran (M88 and Silvercrest) and P&W figures come from Wikipedia or partner and EASA documents.

## Key finding on the starting hypothesis

**Confirmed.** GE's cancelled Affinity, a Mach 1.4-1.6 engine for the Aerion AS2, used a CFM56-derived core:
- Aviation Week (2020): "a high-pressure core adapted from the CFM56 jetliner turbofan and GE F101/F110 military engines".
- The core was a 9-stage HPC with a single-stage HPT.
- The fan was a new 52 in unit, with a bypass ratio of about 3.
- Thrust was given as 18,000 lbf (Aviation Week 2018) or as "20,000-lb class" (Aviation Week 2020). Both values are kept.
- The stated reason for picking this core was its *lower* compression ratio. Leeham estimates that a LEAP-type core flown at Mach 1.4 / 45,000 ft would reach a compressor exit of about 650 °C, "uncomfortably high for a three-hour cruise". Leeham also writes: "This is where the lower compression core of the CFM56 fits."
- GE stopped work on the Affinity in May 2021, when Aerion collapsed (FlightGlobal).

## Summary table (one row per core family)

Notes on the column headings:
- "HPC st." is the number of high-pressure compressor stages. "HPT" is the number of high-pressure turbine stages.
- "TO thrust" is take-off thrust at sea-level static (SLS) conditions, from the EASA TCDS unless stated.
- "Hot limit" is the TCDS take-off limit, taken at the measurement station the TCDS names: EGT (exhaust gas temperature), ITT (inter-turbine temperature) or TGT (turbine gas temperature).

| Core family (engines) | HPC st. / HPT st. | HPC PR | OPR | BPR (parent) | TO thrust (parent) | Dry weight | Hot limit (TCDS, take-off) | Cert. (EASA) / status | Origin & export notes | Supersonic relevance | Gaps | Suitability (**[judgement]**) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **CFM56 / GE F101 "1/9" core**: CFM56-7B, (Affinity), F101, F110; CF34-10E has the same layout | 9 / 1 | ~10 (Leeham, approximate) | 32.7-32.8 (-7B, Wikipedia); "~27" common version (Leeham) | 5.1-5.5 | 9,163-12,143 daN (-7B) | 2,386-2,431 kg (TCDS) vs 5,216 lb (Wikipedia) | EGT 950 °C TO / 925 °C MC, displayed at T49.5 | 17 Dec 1996 (-7B), JAR-E Change 8. Status of new production **not verified** | CFM International is a 50/50 GE (USA) / Safran (France) joint venture. **The core is GE's US-built part.** In 1972 the State Department blocked its export as F101 (B-1) technology. Early cores were built in the US and installed in France in a locked room. Expect US export licensing for a bare core **[inferred]** | **Direct precedent.** Affinity (Mach 1.4-1.6) used this core. The F101 is the supersonic B-1 engine; the F110 (29,000 lb, BPR 0.76) is the F-15/F-16 engine. AIN: Affinity needed "a combustor with advanced coatings optimized for sustained high-speed operations" | No published HPC PR from the OEM, core airflow, Affinity weight or Affinity T4. GE's Affinity page could not be retrieved | **Best technical fit.** It is the lowest-PR core in this thrust class, the only one already engineered for this exact mission, and it has supersonic military heritage. The main risks are US export control and GE's willingness (they cancelled the Affinity in 2021) |
| **GE eCore**: LEAP-1A/1B, Passport 20 | 10 / 2 | 22 (LEAP, Wikipedia); 23 (Passport, TCDS) | 40 (50 top of climb) LEAP; 45 Passport | 9-11 LEAP; 5.6 Passport | LEAP-1A 10,680-14,305 daN; Passport 7,893-8,416 daN | LEAP-1B ≤2,780 kg; Passport 2,065.7 kg | LEAP EGT 1,060 °C TO; Passport EGT 1,035 °C TO | LEAP-1A 20 Nov 2015; LEAP-1B 4 May 2016; Passport (EASA) 18 Dec 2018 | US (GE) core. The US Commerce Department paused LEAP exports to COMAC from May to July 2025. Passport is GE-only | Leeham's thermal estimate (~650 °C compressor exit at Mach 1.4) is the argument *against* this core. The Passport's ceramic-matrix mixer was the basis for the Affinity mixer | No core airflow; no figures for supersonic or high-inlet-temperature operation | **Weaker thermally.** The high HPC PR drives T3 at Mach 1.5 **[inferred]**. Passport's thrust is the right size, but it is US-only and newer, with no supersonic precedent |
| **P&W GTF core**: PW1100G/1500G, PW814/815/812 | 8 / 2 | not found | not found | 12-12.5 (GTF); ~5.5 (PW814, Wikipedia) | PW814GA 6,863 daN; PW815GA 7,122 daN; PW1500G 8,796-10,854 daN | PW814/815 1,408 kg (TCDS) vs 3,135.7 lb (Wikipedia/FAA); PW1500G 2,177 kg | ITT 965 °C (PW814) to 1,083 °C (PW1100G) | PW814/815 31 Aug 2017; PW1500G 18 May 2016 | P&W (USA) / P&WC (Canada). MTU (Germany) holds 15% of PW800, including some HPC stages. EASA "IM." (imported) TCDS | P&W proposed a PW9000 family on the PW1000G core, including a **direct-drive 4:1-BPR** military engine. That is the closest published analogue to an SSBJ cycle. The PW800 already proves a direct-drive, non-geared use of the core | **HPC PR and OPR are unpublished** in every source I read, as is core airflow | **Strong second candidate.** Modern core, right size (PW815 at 16,011 lbf), a precedent for direct-drive medium-BPR use, and some European content. Thermal fit depends on the unknown HPC PR |
| **RR Deutschland BR700 / Pearl** (BR725, Pearl 15, Pearl 700, Pearl 10X with the Advance2 core) | 10 / 2 | **24:1** (Pearl 700, RR) | 43 (Pearl 15); >50 (Pearl 700, projected) | 4.2 (BR725); 4.8 (Pearl 15); >6.5 (Pearl 700) | BR725 75.2 kN; Pearl 15 67.8 kN; Pearl 700 81.2 kN; Pearl 10X >18,000 lbf | BR725 1,635.2 kg; Pearl 700 1,617.1 kg | TGT 900 °C (BR725), 890 °C (Pearl 15), 940 °C (Pearl 700) | BR725 23 Jun 2009; Pearl 15 28 Feb 2018; Pearl 700 14 Sep 2022; Pearl 10X: no TCDS found, flying on the Falcon 10X | **European**: built by Rolls-Royce Deutschland, Dahlewitz, with an EASA (EU state-of-design) TCDS. It is the only European civil core in the 15-20k lbf class. The F130 (BR725) is a USAF B-52 engine | None for supersonic use. RR left Boom's supersonic engine work in 2022 | No core airflow, no OEM BPR/OPR for BR725/Pearl 10X, and no HPC PR for the BR725 (a no-booster layout implies HPC PR ≈ OPR / fan-root PR, i.e. high **[inferred]**) | **Best export and sovereignty position, but thermally the hottest.** A 24:1 HPC gives T3 of roughly 730-880 °C at Mach 1.5 **[inferred, see below]**. It would need heavy derating or an LP pressure ratio near 1.6. Worth a dialogue with RR Deutschland |
| **GE CF34-10** (-10A/-10E) | 9 / 1 | not found | 29 (GE) | not found | 75.44-90.57 kN (-10E) | 2,079 kg (TCDS, includes thrust reverser) | EGT 983 °C TO | 31 Mar 2006 | US (GE) | Same 9-stage + 1-stage layout as the CFM56. Wikipedia says it is "derived from CFM56 [citation needed]"; GE calls it a "clean sheet design" (conflict kept) | HPC PR, airflow and BPR | **Possible lower-risk alternative to the CFM56 core** in the 18-20k lbf class, with the same caveats on US origin. Its lineage is disputed |
| **GE CF34-8** | 10 (single "ten stage axial compressor") / 2 | not found | 28 | not found | 59.16-64.54 kN | 1,227-1,428 kg | (T45 limits; not extracted) | 29 Jun 2000 | US (GE) | None | HPC PR, airflow | **Too small and older.** Low priority |
| **Honeywell HTF7000** (AS907) | 4 axial + 1 centrifugal / 2 | 16 (Wikipedia) | 28.2 (Wikipedia) | 4.2 (Honeywell) vs 4.4 (Wikipedia) | 30.73-34.37 kN | 687-696 kg (TCDS) vs 618.7 kg (Honeywell) | ITT 946-955 °C TO | 22 Oct 2002 | US | None | Core airflow | **Drop.** About 7,500 lbf is too small for any realistic engine count, and the centrifugal last stage is a poor fit for high T3 **[judgement]** |
| **Eurojet EJ200** | 5 / 1 | not found | 26 (MTU) | 0.4 | 13,500 lbf dry / 20,000 lbf reheat (MTU) | ~2,204 lb (MTU) / 989 kg (Wikipedia) | TIT 1,800 K (Wikipedia; no TCDS, military) | Military only (no CS-E certification) | **European** (RR UK, MTU DE, Avio IT, ITP ES; MTU has a 33% development share). Export needs consent from the four governments | Typhoon supercruise: Eurofighter claims Mach 1.5; other sources say Mach 1.1 or 1.21 (all kept). Airflow 75-77 kg/s | Hot-section life at sustained cruise, civil certifiability, HPC PR | **Interesting European option, but a long shot.** The core is small (~13.5k lbf dry, BPR 0.4) and was designed for military life. Civil certification and long-cruise durability are open questions **[judgement]** |
| **Safran M88** | 6 / 1 | not found | 24.5 | 0.3 | 50 kN dry / 75 kN reheat | 897 kg | TET 1,850 K (Wikipedia) | Military | **French** | Qualified with "simulated Mach 1.6 airflows". Rafale supercruise. The core was said to support 73-105 kN. A civil M123/CFM88 derivative was once studied | All Safran data is Wikipedia-only (Safran site blocked) | **Long shot.** Even smaller than the EJ200. The civil-derivative precedent is notable **[judgement]** |
| **GE F414** (X-59) | 7 / 1 | not found | 30 (GE) | 0.25 | 13,000 lbf military / 22,000 lb class | 2,445 lb max | not found | Military | US ITAR (India co-production needed State Department and Congress notification) | The F414-GE-100 powers NASA's X-59. The Gripen demonstrator supercruised at Mach 1.2 | Hot-section limits, durability | **Unattractive** for a European operator (ITAR) and too small **[judgement]** |
| **GE F404** (reference) | 7 / 1 | not found | 26-28 (GE) | 0.34 | 11,000 lbf military / 17,700-19,000 lb class | 2,282 lb | not found | Military | US ITAR | Supersonic fighter and trainer engine | n/a | Reference only |
| **Safran Silvercrest** | 4 axial + 1 centrifugal / 1 | "over 17" (2007 design) | 38.5 | 5.9 | 11,450 lbf | (Wikipedia figure is computed, not recorded) | n/a | **Cancelled** in development | French | None. Its problems included **HPC operability** | n/a | **Drop.** Cancelled, with core problems |
| *Context:* Boom Symphony | clean-sheet | - | - | medium | 40,000 lbf, Mach 1.7 target | - | - | Development | US | Boom is vertically integrating the engine. Per Wikipedia, GE's Affinity cancellation left "no supersonic turbojet supplier for the Boom Overture", and RR also withdrew | - | Not a purchasable core |

## Illustrative compressor-exit temperature at Mach 1.5 **[inferred]**

All values below are my own calculation; no source states them.

- **Assumptions:** ISA above 11 km. T2 = 216.65 × (1 + 0.2 × 1.5²) = 314 K. Fan-root/booster pressure ratio (our in-house LP) of 1.6, 2.0 or 2.5. HPC at its take-off-class PR. Polytropic efficiency 0.90.
- **Cross-check:** this method gives about 700 °C for a LEAP-like OPR of 40 at Mach 1.4, against Leeham's ~650 °C, so it reads slightly high.

| HPC PR | example core | T3 (°C), LP PR 1.6 | LP PR 2.0 | LP PR 2.5 |
|---|---|---|---|---|
| 10 | CFM56 (Leeham, approximate) | 484 | 540 | 600 |
| 16 | HTF7000 | 606 | 671 | 740 |
| 22 | LEAP | 700 | 771 | 848 |
| 23 | Passport | 714 | 786 | 864 |
| 24 | Pearl 700 / Advance2 | 727 | 800 | 879 |

**Reading [judgement]:**
- A low-PR core lets the in-house LP system keep a healthy pressure ratio, and so specific thrust and cruise SFC, while holding T3 near today's subsonic take-off values.
- A high-PR core forces either a weak LP system or sustained very high T3.
- At cruise the HPC actually runs at reduced corrected speed and so at lower PR, so these are upper-bound indications only.

## Biggest gaps

1. **HPC pressure ratio and core (HP) airflow** are unpublished for almost every candidate. The only published HPC PR figures are Passport 23 (TCDS), Pearl 700 24 (RR) and LEAP 22 (Wikipedia); the CFM56's ~10 is only Leeham's approximation. The PW800/GTF and CF34-10 have neither. These two numbers decide core sizing, so OEM data under NDA is needed.
2. **No sourced T4 or T3 limits** for the civil cores. TCDS give only EGT, ITT or TGT at different stations, so they are not directly comparable.
3. **No primary GE data on the Affinity.** The GE page could not be retrieved (only via Wikipedia), and the Aviation Week articles were paywalled beyond their leads. Affinity's weight, OPR, T4 and the extent of its core modifications are unknown.
4. **Export classification** (EAR ECCN vs ITAR) of a stand-alone CFM56, eCore or PW800 core is not stated in any source. Only the history (the 1972 F101 core export block) and the 2025 LEAP/COMAC pause were found.
5. **CFM56 production status** in 2026 is not verified.
6. **Pearl 10X certification status and OPR** were not found. There is no EASA TCDS in search.
7. **Durability at sustained high inlet temperature.** No source quantifies life impact for any civil core. Military cores (EJ200, M88) have supersonic heritage but no civil life data.
8. Safran, P&W/P&WC and CFM sites blocked automated access. These figures rely on Wikipedia, MTU and EASA, and should be re-checked by hand.
