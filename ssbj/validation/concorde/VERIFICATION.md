# Concorde reference data: page verification (2026-10-04)

Detail, exact quotes and URLs are in `sources_verified.yaml` (101 entries). The Aerion AS2 checks are in `../aerion_as2/sources_verified.yaml` (42 entries).
"Verified" means the figure was read on the page itself, either HTML or PDF. A computer check confirmed that every HTML quote appears word for word in the fetched page text. The ICAS 1976 paper is a scanned PDF with no text layer, so I read it from page images.

## Figures used in case.yaml / reference.yaml

| Figure (file) | Old value (snippet) | Verified value and source | Changed? |
|---|---|---|---|
| Range at max fuel (ref gate) | 3,550 nmi, 8,845 kg, "FAR reserves" | 3,550 nmi: Heritage airframe-performance, "Range with max fuel, FAR reserves and 8,845 kg (19,500 lb) 3,550 n miles". The word "payload" is not on the page, and the page does not define the reserves | No (value). Caveat added |
| Max fuel (ref gate) | 95,680 kg; alt. 94,470 / 95,430 | 95,680 kg (Heritage weights; Wikipedia). 94,470 kg / 119,280 L is on **/fuel-addcap**, not /fuelgeneral as cited. **New alternative: 95,254 kg** (Heritage Concorde 'B' page). 95,430 (PPRuNe) not verifiable (403) | No (value). Source URL corrected; one alternative added |
| OEW (diagnostic) | 78,700 kg | 78,700 kg (Heritage weights; Wikipedia, where it is labelled "Empty weight") | No |
| Cruise TSFC (diagnostic) | 1.195 lb/(lbf h) | 1.195 (Wikipedia Olympus, marked **[citation needed]**, conditions not given; the Heritage page repeats the same block) | No (value). Still unsupported |
| Cruise L/D (diagnostic) | 7.14-7.5 | 7.14 at M2.04 (Wikipedia Concorde spec block, no inline citation). 7.5 at M2 is in the **Lift-to-drag ratio** article, citing Orlebar 1997 p.116, not in the Concorde article. The same article also says "about 7 at Mach 2" | No |
| Engine dry mass (diagnostic) | 3,175 kg | 3,175 kg (Wikipedia Olympus, "Data from Jane's"; Heritage) | No |
| LHR-JFK fuel load (diagnostic) | 93-96 t (PPRuNe) | Not verifiable (PPRuNe 403). No reputable trip-fuel source found | Gap |
| MTOW (case) | 185,070 kg | 185,070 kg (Wikipedia, 408,010 lb). **Heritage and Aerospaceweb give 185,065 kg (408,000 lb)** | 5 kg difference, immaterial |
| Max landing (case) | 111,130 kg | 111,130 kg (Heritage. Wikipedia labels it "Gross weight") | No |
| Fuel capacity (case) | 95,680 kg | as above | No |
| Dry SLS thrust (case) | 139.4 kN | 139.4 kN (Wikipedia Olympus; Heritage spec block). **Conflicts:** Heritage variants list "32,000 lbf (142 kN) dry"; Wikipedia Concorde infobox "31,000 lbf (140 kN)" | No (value). Conflicts recorded |
| Reheat SLS thrust (case) | 169.2 kN | 169.2 kN (Wikipedia Olympus; Heritage). Concorde infobox: 169.3 kN | No |
| OPR (case) | 15.5 | 15.5:1 "with aircraft stationary" (Wikipedia Olympus; Heritage). New: the engine-only ratio at M2.0 / 51,000 ft is 11.3:1 | No |
| SLS airflow (case, T4 match) | 186 kg/s "Wikipedia/Heritage" | 186 kg/s **only on Wikipedia Olympus** ("Air mass flow: (186 kg (410 lb))/s)", no condition). **Not on the Heritage engine page** | Value same. Attribution corrected |
| Crew (case) | 9 (concordesst "100 pax + 9 crew") | **Not verified**: concordesst returns 403. Pages read give flight crew = 3 (Wikipedia; ICAS 1976 p.569). No cabin-crew number was found on any page | **Unverified; flagged** |
| Fuel tanks (case) | 13 | 13: Heritage fuelgeneral ("thirteen sealed tanks") and the /fuel-addcap table. Tanks 9-11 capacities are now verified from the page, not from SUAVE | No |
| Fin area / base chord (case) | 33.91 m2 / 10.59 m | 33.91 m2 (excl. dorsal) / 10.59 m (Heritage airframe-dimensions) | No |
| Wing gross area (case) | 358.25 m2 | 358.25 m2 (Heritage; Wikipedia). Heritage also gives AR 1.7 and a root reference chord of 27.66 m. The case root chord is 29.907 m (definition may differ) | No |
| Wing span (case, implied 25.6 m) | 25.56 / 25.6 m | 25.56 m (Heritage), 25.6 m (Wikipedia) | No |
| Fuselage length (case) | 61.66 m | 61.66 m (Wikipedia). Heritage gives 62.10 m as *overall* length | No |
| Fuselage max diameter (case 3.1 m, SUAVE) | Heritage width 2.88 m; external height 1.96 m (snippet) | Wikipedia: 2.87 m wide by **3.30 m high** external. The 1.96 m "external height" on the Heritage page equals the cabin height and is a page error. The equal-area circle of 2.87 by 3.30 m is 3.08 m (arithmetic), consistent with 3.1 m | Snippet value 1.96 m wrong. Case value still fine |
| Control-surface area (case 36 m2, ASSUMPTION) | none | **Elevons 32.00 m2 + rudder 10.40 m2 = 42.40 m2** (Heritage dimensions) | **Sourced value differs from the case assumption** |
| Cruise Mach (case) | 2.0 | ICAS 1976 p.566: "Best range cruise ... cruise climb at M = 2.0 at maximum continuous power". Wikipedia: M2.02. Heritage: max cruise M2.04 | No. Now manufacturer-sourced |
| Cruise altitude min / max (case 50,000 / 60,000 ft) | forum snippets / Heritage | ICAS 1976 p.566: on the North Atlantic, cruise "would start at 50,000 ft. and reach 57,000 ft. by the end of cruise". In the tropics it runs from 53,000 ft to the "maximum authorised altitude of 60,000 ft". Heritage: ceiling 60,000 ft | No. Note the North Atlantic cruise ends near 57,000 ft |
| Reserves (case: 10 % trip, 200 nmi alternate, 30 min at 1,500 ft) | assumption | **14 CFR 121.645(b) text read** (eCFR): 10 % of the flight *time*, then fly to the *most distant alternate specified* (**no fixed distance**), then 30 min hold at 1,500 ft above the alternate at standard temperature. In force since 1964 | **The 200 nmi alternate and the "10 % of trip fuel" reading are not in the rule**. They remain assumptions |
| Field length (case, reported only) | 11,200 ft | 3,410 m (11,200 ft) to 35 ft (Heritage) | No |
| Profile (case, ASSUMPTION) | none | ICAS 1976: climb at Vmo; best subsonic cruise M0.95 at about 27,000 ft at heavy weights; reheat off at M1.7; 20 % of the trip fuel is burned by the start of cruise, when 9 % of the distance is covered | Supports the assumed profile (case uses 28,000 ft / M0.95 / M1.7) |

## Figures where the verified value differs from what case.yaml / reference.yaml use
1. **Crew = 9**: the 9 is unverified. Only a flight crew of 3 was found on any page.
2. **Reserve detail**: the 200 nmi alternate distance is not part of FAR 121.645, and the contingency is 10 % of flight time, not of trip fuel. The Heritage page does not say which "FAR reserves" it means.
3. **control_surface_area_m2 = 36**: the page sum is 42.4 m2 (elevons plus rudder).
4. **MTOW 185,070 vs 185,065 kg** (Heritage): negligible.
5. **Attributions**: 94,470 kg comes from `/fuel-addcap`, not `/fuelgeneral`. The 186 kg/s airflow is on Wikipedia only, not Heritage. The 7.5 L/D comes from the Lift-to-drag ratio article.

## Payload-range data found (no diagram found)
- 8,845 kg at 3,550 nmi, max fuel, "FAR reserves" (Heritage).
- Max payload at 2,760 nmi, "FAR reserves: at M0.95 at 9,100 m (30,000 ft)" (Heritage; reads as all-subsonic).
- Max payload at 3,365 nm (6,230 km), conditions not given (Aerospaceweb). The same page gives max fuel at 3,560 nm.
- Range 3,900 nmi with no conditions (Wikipedia; Heritage "Maximum Permissible Range").
- Max payload is internally inconsistent on the Heritage weights page: 13,380 kg and 12,700 kg. Typical payload is 11,340 kg.
- Arithmetic check: MTOW 185,070 − OEW 78,700 − fuel 95,680 = 10,690 kg. That is above 8,845 kg, so the 3,550 nmi point is not MTOW-limited if those figures go together. The page does not explain the difference.

## Remaining gaps
- **FAA TCDS A45EU not read.** concordesst.com returns 403, web.archive.org connections are reset, and the drs.faa.gov document API returns 403. No EASA TCDS for Concorde was found.
- **Leyman 1986** (Prog. Aerosp. Sci. 23:185-238) is paywalled; the core.ac.uk copy is blocked.
- No Concorde payload-range diagram, and no reserve-policy definition behind the 3,550 nmi figure.
- No reputable LHR-JFK trip or block fuel figure. Distance is 2,999 nmi (WGS84, computed from Wikipedia airport coordinates). Wikipedia's operational-history article uses a 3,050 nmi London-New York sector. Wikipedia gives cruise consumption of 4,800 US gal/h at M2 and 60,000 ft (citing Allen 2012).
- Cruise SFC has no stated conditions or primary source. The L/D values have no weight or altitude conditions.
- NASA TM-75238 (Airbus/Concorde flight vs tunnel drag) was fetched, but its OCR is too garbled to extract numbers.
- ICAS 1976 pp.570-571 not read (pilot narrative). pp.563-569 read.
