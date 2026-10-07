# Concorde / Aerion AS2 validation data: gaps and source quality

Retrieved 2026-10-04. Companion files: `sources_raw.yaml` (Concorde) and `../aerion_as2/sources_raw.yaml`.

## Overall caveat
- **No web page was read directly.** Every WebFetch failed (egress proxy). All web figures are `search_snippet`. These are LLM summaries of search-result pages, so the exact URL behind a figure is inferred. I restricted searches to one domain (`allowed_domains`) to pin attribution where I could. The filter still leaked some uspto.gov patent links.
- A few queries included a candidate value, and the snippet may just repeat it. Those entries are flagged in `notes` ("Search query contained a candidate value").
- I read the SUAVE `Concorde.py` vehicle file directly through `git clone` from github.com. Those values are model inputs from an open-source design code, not primary data (`code_model_input`).

## Reachable vs blocked hosts
| Host | Status |
|---|---|
| WebSearch (US results) | works |
| github.com via `git clone` (public repo) | reachable (SUAVE cloned) |
| `gh api` on repos not attached to the session | 403 (needs add_repo) |
| pypi.org / files.pythonhosted.org | reachable (installed rapidocr, pymupdf into /home/user/venv) |
| heritageconcorde.com, globalsecurity.org, aerospaceweb.org, flugzeuginfo.net, web.archive.org, easa.europa.eu, api.semanticscholar.org, baesystems.com, arc.aiaa.org, aiaa.org, grahamswebdesign.com, gracesguide.co.uk, fredstarr.com, drs.faa.gov | **blocked** (WebFetch EGRESS_BLOCKED / "unable to fetch") |
| en.wikipedia.org, ntrs.nasa.gov, openvsp.org, concordesst.com | blocked (per task brief / proxy log; not retried) |

I did not try sciencedirect, researchgate, flightglobal or the UK CAA. Every host I did try was blocked.

## Local textbooks
- **Anderson, Introduction to Flight**: gives t/c 3% at the root and 2.15% from the nacelle outward (p.392), length 202 ft (Prob. 5.20, p.437), cruise 1936 ft/s at 50,000 ft (Ex. 4.14, p.171). It also says cruise is Mach 2.2 (pp.391, 437), which conflicts with every other source.
- **Anderson, Fundamentals of Aerodynamics**: Mach 2 at 50,000 ft (p.685).
- **Anderson & Eberhardt, Understanding Flight**: Mach 2 at 55,000 ft (p.12), turbojet (p.126), about 500 lb of fuel per seat-hour (p.240).
- **Megson**: materials only (RR58/CM001 alloy). No figures recorded.
- **Raymer, 2nd ed. 1992**: the PDF is a scanned image (2 book pages per PDF page) with no text layer, and the scan has no index. I OCR'd selected pages (end matter and the supersonic-drag pages, book pp.156-159 and 290-293). The only relevant item is the generic SST wave-drag efficiency E_WD of 1.4–2.0 (p.293). I found **no Concorde-specific data in Raymer**. A full OCR (~11 s/page, about 70 min) was not run.

## Missing (no source found)
- Component weight breakdown (wing, fuselage, systems, etc.). Only engine dry weight is known: 3,175 kg each, from Wikipedia.
- Typical 100-pax payload **mass** and the per-passenger allowance.
- Detailed reserve policy. Only "FAR reserves" is stated.
- LHR–JFK **trip fuel** from a primary source. There are only forum and Q&A figures: ramp fuel 90–96 t, trip about 77 t.
- CD0 vs Mach, drag polar, and wave-drag coefficient on a defined reference area.
- Primary (flight-manual) start and end altitudes for the cruise climb.
- Olympus SFC at SLS separately for dry and reheat, and cruise thrust from a citable source.
- Root chord, tip chord, MAC and sweep breakdown from primary data. SUAVE is the only source.
- Total aircraft wetted area from a pinned source. 13,196 ft² is unattributed.
- Aerion AS2: bypass ratio, exact Affinity thrust, and a single consistent MTOW/range set for one design iteration.

## Weakly sourced (single or unattributed snippet)
- Cruise thrust 10,030 lbf per engine at M2/53,000 ft/ISA+5. The source is probably the Wikipedia Olympus 593 article; unconfirmed.
- Fuel flows (5 t/h per engine at 50 kft, 4.2 t/h at 60 kft, 25 t/h per engine at take-off): PPRuNe forum only.
- Wetted area 13,196 ft² with S = 4,151 ft²: unattributed, and S does not match the 3,856 ft² reference area.
- Mach 2 drag components (CDw,lift ~0.001, CDi ~0.004, "fuselage volume drag ~0.025"): unattributed, reference area unknown. Do not use.
- Approach speed 165 kt and TOFL 11,300 ft: simviation and similar sites.
- Range at max payload of 2,760 nmi, which the snippet ties to "M0.95 at 30,000 ft". This may be garbled; verify.
- Heritage "max wing loading 488 kg/m² (1,000 lb/ft²)": internally inconsistent. MTOW/S gives 516.6 kg/m².
- Heritage "fuselage max external height 1.96 m": the same number as cabin height, so probably an error. SUAVE uses 3.32 m.

## Conflicts recorded
- **Length:** 62.10 m (Heritage) vs 61.66 m (Wikipedia, SUAVE) vs 202 ft = 61.6 m (Anderson).
- **Span:** 25.56 m (Heritage) vs 25.6 m (Wikipedia, SUAVE).
- **Height:** 11.40 m (Heritage) vs 12.2 m (Wikipedia).
- **MTOW:** all sources give 408,000 lb, but the kg figure varies: 185,065 kg (Heritage), 185,070 kg (Wikipedia, FAA TCDS snippet), 185,000 kg (concordesst, SUAVE).
- **Fuel capacity:**
  - 95,680 kg (Heritage weights page, Wikipedia)
  - 94,470 kg / 119,280 L (Heritage fuel page; also the sum of the tank table used in SUAVE)
  - 95,430 kg (PPRuNe)
  - volume 119,600 L (Wikipedia)
- **Reheat thrust:** 38,050 lbf (Heritage) vs 38,000 lbf (Wikipedia). Both give 169.2 kN.
- **Dry thrust:** 31,350 / 31,300 / 31,000 lbf.
- **L/D at Mach 2:** 7.5 (Wikipedia) vs 7.14 at M2.04 (Wikipedia table) vs ~7.3 (Starr, from the Concorde B comparison) vs "about 7" (unattributed).
- **Subsonic L/D:** 12 at M0.95 vs 11.47 at M0.94.
- **Cruise Mach:** 2.0 / 2.02 / 2.04 max (Heritage) vs 2.2 (Anderson, Introduction to Flight).
- **Outboard t/c:** 2.15% (Anderson) vs 3% constant (SUAVE).
- **Takeoff distance:** 3,410 m / 11,200 ft (Heritage) vs 3,430 m / 11,300 ft (simviation and similar).
- **Range:** 3,550 nmi (max fuel, 8,845 kg payload, FAR reserves; Heritage) vs 3,900 nmi (Wikipedia, conditions unstated) vs about 4,500 statute miles with 100 pax + 9 crew (concordesst).
- **Aerion AS2:**
  - MTOW: 121,000 lb (BJT/AW) vs 150,000 lb (Wikipedia) vs 115,000 lb (New Atlas 2014)
  - supersonic range: 4,200 nmi vs 4,750 nmi
  - length: 145 ft vs 160 ft
  - engine thrust class: 15,000 vs 20,000 lbf
  - cruise Mach: 1.4 vs the original 1.6

## Suggested next steps if access improves
- Read the FAA TCDS A45EU (concordesst.com/A45eu.pdf, or the docket copy at data.ntsb.gov) for weights, CG limits and fuel.
- Read Leyman (1986), Prog. Aerospace Sci. 23(3):185–238, for L/D, drag breakdown and the planform.
- Read the Wikipedia Concorde and Olympus 593 pages directly to confirm the snippet figures and get their underlying citations.
