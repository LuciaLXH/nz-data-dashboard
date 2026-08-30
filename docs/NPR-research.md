# Water NZ National Performance Review (NPR) — Data Extraction for 6 Regions

**Prepared:** 2026-08-30 · **Status:** complete (cross-checked against supplier annual reports and Water NZ/Taumata publications)

**Purpose:** per-capita water use and leakage figures for the water suppliers serving the 6 target
regional-council areas: Auckland, Canterbury, Otago, Hawke's Bay, Southland, Waikato.

---

## 0. Executive summary — what the NPR actually is (important)

- The **Water New Zealand National Performance Review (NPR) ended at the 2021/22 edition**
  (published ~March 2023, the "final review by Water New Zealand" — see
  [Water NZ story: Water supply is a postcode business](https://www.waternz.org.nz/Story?Action=View&Story_id=1940)).
  There is **no newer Water NZ NPR** (as of 2026-08-30).
- From 2023, drinking-water performance reporting became **regulated** and is published by
  **Taumata Arowai (Water Services Authority)** in the **Network Environmental Performance Report
  (NEPR)** series. The **latest is NEPR 2024/25 (published June 2026)**, which also has a
  **public unit-level data extract** on data.govt.nz.
- Therefore: **"latest NPR-style data" for every supplier below = NEPR 2024/25** (all 9 target
  suppliers present), with **NPR 2021/22** (final Water NZ edition, public dashboard data) and
  **NPR 2020/21** (for Auckland & Hastings, absent from the final edition) as the Water-NZ-sourced
  comparison. All three are fully quoted below.

---

## (a) Sources found (URLs)

### Water New Zealand NPR (final edition 2021/22 + earlier)
| Source | URL | Access |
|---|---|---|
| NPR portal (Publication + Dashboard 2021/2022 + Previous Years Reports) | https://www.waternz.org.nz/NationalPerformanceReview | Public page; report PDFs require Water NZ login |
| NPR "Resource Efficiency" Tableau dashboard (public workbook) | https://public.tableau.com/views/ResourceEStory2022/ResourceEFS | Public (data downloaded via `https://public.tableau.com/workbooks/ResourceEStory2022.twb`) |
| NPR 2021/22 media release: "Water consumption continues to rise" | https://www.waternz.org.nz/Story?Action=View&Story_id=1939 | Public |
| NPR 2021/22 media release: "Water supply is a postcode business" (confirms final NPR, 2021/22 coverage) | https://www.waternz.org.nz/Story?Action=View&Story_id=1940 | Public |
| NPR 2020/21 media release (Scoop, 15 Mar 2022): 281.8 L/person/day national; Auckland 146 L/person/day | https://www.scoop.co.nz/stories/print.html?path=AK2203/S00299/huge-regional-disparities-in-water-wastage-new-npr-report.htm | Public |
| NPR 2021/22 analysis: Newsroom "Why NZ (really) needs water reform – in five charts" (26 Mar 2023) | https://newsroom.co.nz/2023/03/26/why-we-really-need-water-reform-in-five-charts/ | Public |

> Note: the NPR report PDF itself (e.g. `Attachment?Action=Download&Attachment_id=5573` = 2020/21,
> `Attachment_id=3142` = 2016/17 Vol 1) is **members-only** (login wall confirmed 2026-08-30).
> However Water NZ published the full underlying **participant-level dataset in the public Tableau
> dashboards**; the CSV extract used here was pulled from
> `ResourceEStory2022.twb` → `federated.hyper` (574 rows, 9 reporting years 2013/14–2021/22).

### Taumata Arowai — Network Environmental Performance Reports (successor to NPR)
| Source | URL | Access |
|---|---|---|
| NEPR 2024/25 report (June 2026, 55 pp) | https://www.taumataarowai.govt.nz/assets/Uploads/Network-Performance/Network-Environmental-Performance-Report-2024-25.pdf | Public PDF |
| NEPR 2024/25 unit-level data (data.govt.nz, **CC BY 3.0 NZ**) | https://catalogue.data.govt.nz/dataset/network-environmental-performance-report-24-25 | Public CSV (DW_Network/DW_Org/DW_Abs/DW_Consent + WW_*) |
| NEPR 2024/25 factsheet | https://www.taumataarowai.govt.nz/assets/Uploads/Network-Performance/Factsheet-2024-25-NEPR.pdf | Public PDF |
| NEPR 2023/24 report (June 2025, 80 pp; per-council Figures 29–31) | https://www.taumataarowai.govt.nz/assets/Uploads/Network-Performance/Network-Environmental-Performance-Report-2023_24.pdf | Public PDF |
| NEPR index page | https://www.taumataarowai.govt.nz/about-us/reports-and-publications/water-services-insights-and-performance | Public |

### Local copies saved in this repo
- `data/raw/waternz_npr/npr_2013-2022_dashboard_extract.csv` — full NPR dashboard dataset
  (all participants × 2013/14–2021/22, key drinking-water measures)
- `data/raw/taumata_nepr/NEPM Final Data Extract for Release 27072026 *.csv` — NEPR 2024/25 unit-level data (all files)
- `data/raw/taumata_nepr/Network-Environmental-Performance-Report-2024-25.pdf` and `...-2023-24.pdf`

---

## (b) Data tables

### Table 1 — Latest official figures: NEPR 2024/25 (reporting year 1 Jul 2024–30 Jun 2025; published June 2026)

Metrics, exact field names as published in the NEPM data extract (DW_Network.csv / DW_Org.csv):

| Supplier (territorial authority / CCO) | Region | Population served (`D-EH3`) | Connections (res + non-res, `D-EH1.1`+`D-EH2.1`) | Water supplied (`D-EH4`, m³/yr) | **Water supplied ≈ L/person/day** (derived) | **Median residential consumption** (`D-RE4`, L/connection/day, main network) | **Water loss** (`D-RE1` ÷ `D-EH4`, %) | **CARL** (`D-RE2.1`, L/connection/day, derived) | **ILI** (`D-RE3`, main network) | **Residential metering** (`D-RE6` ÷ `D-EH1.1`) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Watercare** (Auckland) | Auckland | 1,663,170 | 480,944 | 163,082,049 | **268.6** | 490 (main AUC003) | **19.7%** | 173.7 | 2.3 | **99.9%** |
| **Christchurch City Council** | Canterbury | 387,390 | 169,906 | 51,914,528 | **367.2** | 411 (main CHR009) | **30.0%** | 239.7 | 4.32 | 93.5% |
| **Selwyn District Council** | Canterbury | 70,840 | 26,678 | 9,205,835 | **356.0** | 615 (main Rolleston) | **17.6%** | 153.1 | 1.6 (Rolleston) | 83.6% |
| **Waimakariri District Council** | Canterbury | 54,374 | 22,426 | 7,752,711 | **390.6** | 459.7 (main Rangiora) | **24.3%** | 230.4 | 3.33 (Rangiora) | 29.0% |
| **Dunedin City Council** | Otago | 115,357 | 50,251 | 16,210,080 | **385.0** | 677 (main DUN001; conf: very uncertain) | **18.6%** | 78.4 | 0.87 | 0.8% |
| **Invercargill City Council** | Southland | 50,197 | 21,469 | 8,104,727 | **442.4** | 224 (main INV001) | **17.0%** | 120.8 | 2.2 | 3.2% |
| **Napier City Council** | Hawke's Bay | 62,992 | 24,997 | 9,978,980 | **434.0** | 555 (main NAP001NA) | **22.6%** | 197.3 | 4.0 | 3.4% |
| **Hastings District Council** | Hawke's Bay | 69,959 | 24,599 | 17,253,884 | **675.7** | 717.8 (main HAS001) | **26.3%** | 434.4 | 5.68 | 13.3% |
| **Hamilton City Council** | Waikato | 192,000 | 65,083 | 22,362,344 | **319.1** | 650 (main HAM001) | **14.9%** | 139.8 | 3.1 | res meters n/r (blank) |

**Also published in NEPR 2024/25 report (Appendix 2, Figure 18/19/20), per council:**
- Water supplied to network, L/connection/day (Figure 18): Hastings **1,922** · Hamilton **941** ·
  Watercare **929** · Dunedin **884** · Christchurch **837** · Selwyn **945** · Waimakariri **947** ·
  Napier **1,094** · Invercargill **1,034**.
- Current Annual Real Loss, L/connection/day (Figure 19, as plotted, pairings verified against the
  raw extract): Christchurch **240** · Waimakariri **230** · Hastings **436** · Napier **197** ·
  Watercare **174** · Selwyn **153** · Hamilton **140** · Invercargill **121** · Dunedin **79**.
  *(Figure 19 plots CARL per connection/day; the CSV-derived values in Table 1 use the same fields and agree within rounding.)*
- Residential water use per connection per day (Figure 20, estimated): Hamilton **683** · Watercare
  **568** · Dunedin **555** · Christchurch **440** · Hastings **1,224** · Invercargill **594** ·
  Napier **628** · Selwyn **683** · Waimakariri **639**.

*Note: "Auckland Council" also appears in the NEPR data — these are 15 small regional-park/camping
supplies (pop ≈ 6,000 total), NOT the Auckland metro network. The Auckland metro network is Watercare.*

### Table 2 — Final Water New Zealand NPR 2021/22 (reporting year 2021/22; published ~March 2023; dashboard data)

Exact field names as in the NPR dashboard data. "L/person/day" = `WSB5` (Water Supplied to the
drinking water network, m³/yr) ×1000 ÷365 ÷ `WSB1a` (population served) — the NPR per-capita supply metric.

| Supplier | Region | Year | Pop served (`WSB1a`) | Connections (`WSB4`) | Water supplied (`WSB5`, m³/yr) | **Water supplied ≈ L/person/day** | Avg daily residential consumption (`WSB8`, L/conn/day) | Total loss (`WSE1a`, m³) | % loss (`WSE1b`, 2020/21 col.) | CARL (`WSE1d`) | ILI (`WSE1h`) | Res metering % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Watercare/Auckland | Auckland | **2020/21** (absent from 2021/22) | 1,590,000 | 489,612 | 139,151,318 | **239.8** | 510.2 | 20,253,478 | **14.6%** | 132.8 | 6.19 | **100%** |
| Christchurch CC | Canterbury | 2021/22 | 381,764 | 160,969 | (not reported 2021/22) | — | n/r | 13,286,197 | 22.3% (2020/21) | 279.8 | 4.10 | 92.4% |
| Selwyn DC | Canterbury | 2021/22 | 50,113 | 22,284 | 8,240,854 | **450.5** | 914.1 | 1,281,361 | 20.5% (2020/21) | 145.0 | 1.7 | 97.8% |
| Waimakariri DC | Canterbury | 2021/22 | 52,711 | 21,116 | 7,072,854 | **367.6** | 683.7 | 1,958,841 | 24.9% (2020/21) | 263.0 | 3.0 | 24.4% |
| Dunedin CC | Otago | 2021/22 | 114,273 | 48,841 | 16,156,801 | **387.4** | 564.2 | 3,566,490 | 21.6% (2020/21) | 216.9 | 2.16 | 0.3% |
| Invercargill CC | Southland | 2021/22 | 49,641 | 20,548 | 8,296,740 | **457.9** | −825.6 (bad data) | 1,153,240 | 9.6% (2020/21) | 136.0 | 2.98 | 1.1% |
| Napier CC | Hawke's Bay | 2021/22 | 66,700 | 24,028 | 8,511,025 | **349.6** | 650.0 | 1,293,653 | 16.0% (2020/21) | 130.0 | 2.9 | 3.1% |
| Hastings DC | Hawke's Bay | **2020/21** (absent from 2021/22) | 66,318 | 26,217 | 14,255,518 | **588.9** | 824.1 | 4,248,800 | **29.8%** | 520.0 | 5.53 | 4.9% |
| Hamilton CC | Waikato | 2021/22 | 178,500 | 62,013 | 21,523,902 | **330.4** | 649.7 | 3,359,713 | 15.8% (2020/21) | 144.0 | 3.0 | 0.5% |

*National context (NPR 2021/22 press release): average NZ property ≈ 213,000 L/yr; ~20% of drinking
water lost in pipes; 33 of 64 providers participated. NPR 2020/21 release: national average
281.8 L/person/day; Auckland (fully metered) 146 L/person/day residential use; >100M m³ lost ≈ 20% of supply.*

*Derived 2021/22 loss % (= `WSE1a` total loss ÷ `WSB5` water supplied, not published as `WSE1b` in the
extract): Dunedin 22.1% · Hamilton 15.6% · Napier 15.2% · Invercargill 13.9% · Selwyn 15.5% ·
Waimakariri 27.7% · Christchurch n/r (WSB5 not reported).*

### Table 3 — National context (Taumata Arowai NEPR, published)
| Metric | 2023/24 | 2024/25 |
|---|---|---|
| Median household water use (L/connection/day) | 604 | **678** |
| National residential metering | 57% | **61%** (metro 69%, provincial 49%, rural 40%) |
| National non-residential metering | 75% | **82%** (metro 91%) |
| Median CARL (L/connection/day) | 185 | (see report) |
| Total reported water loss | 162M m³ ≈ 29% of supply of respondents (2023/24) | ~159M m³ across densities (2024/25, Fig. 9) |
| ILI: % networks <2 / ≥4 | — | 27% / 36% (2024/25) |

### Table 4 — Supplier-published figures (council Annual Reports / DIA mandatory measures / Watercare AR)
Cross-checks extracted from the suppliers' own documents (subagent-verified; exact metric names quoted).
These use **different bases** from Tables 1–2 (see caveats 9–12).

| Supplier | Year | L/person/day (as published) | Real loss % (as published) | Metering (as published) | Population / connections (as published) | Source |
|---|---|---|---|---|---|---|
| Watercare (Auckland) | FY2024/25 | **257 L/person/day** gross per-capita (incl. commercial; target 247–259) | **12.8%** network water loss (target <13%); **119.2 L/conn/day** real loss (SOI measure) | ~100% (all households metered) | ~1.7 million | [Watercare AR 2025](https://www.aucklandcouncil.govt.nz/content/dam/ac/docs/reports/ccos/watercare-annual-report-2025.pdf) pp.14, 87, 95; [ComCom trends 2025](https://www.comcom.govt.nz/assets/Documents/crown-monitor/Watercares-performance-trends-2025-edition-28-November-2025.pdf) |
| Christchurch CC | 2025 (AR) | **239 L/resident/day** (DIA measure 5; target ≤220; 2024: 298, 2023: 261) | **28.6%** real water loss (DIA measure 2; target ≤25%; 2024: 29.2%, 2023: 27.3%) | ≈99.9% of connections metered per WSP (130,612/130,707) — legacy meters, limited volumetric charging | 389,299 (WSP 2019/20); 130,707 conns (WSP; AR2025 says ~170,000, different basis) | [CCC AR 2025 LOS](https://christchurch.infocouncil.biz/Open/2025/10/CNCL_20251030_ATT_10656_EXCLUDED.PDF) pp.98, 104; [Christchurch WSP](https://fyi.org.nz/request/28299/response/109012/attach/6/Water%20Safety%20Plan%20WSP%20Volume%20B%20Christchurch%20Lyttelton%20Current%20version%20Optimized.pdf) |
| Selwyn DC | 2020/21 (NPR, via council news) | **296 L/person/day** (5-yr avg prior 379; natl avg 282) | NEPR 2023/24: **35 L/conn/day** real loss ("among the lowest in NZ") | **100%** universal metering (rollout 2015–2018) | ~30,000 households + 8,000+ businesses | [Selwyn news Apr 2022 (Wayback)](http://web.archive.org/web/20260201221859/https://www.selwyn.govt.nz/news-And-events/news/archived/selwyn-water-systems-continue-to-rank-among-the-best-2022); [Selwyn charges](https://www.selwyn.govt.nz/services/water/water-supplies/your-water-charges) |
| Waimakariri DC | 2025 (planning estimate) | **319 L/person/day incl. leakage; 260 excl.** | 25% avg leakage (2019 assessment: 239 L/conn/day, ILI 2.7 Band B); NEPR 2023/24 35 L/conn/day (low-confidence) | ≈0% residential (no universal metering; ~114 special meters + bulk meters) | 56,100 serviced FY2024/25; 22,425 DW connections | [Waimakariri WSP Assessment](https://www.waimakariri.govt.nz/__data/assets/pdf_file/0038/186896/Assessment-of-Drinking-Water-Services-WSP-Report.PDF) p.34; [WSDP 2025](https://www.waimakariri.govt.nz/__data/assets/pdf_file/0027/178047/Local-Water-Done-Well-Water-Services-Delivery-Plan-For-DIA-Review-and-Acceptance-07.07.2025.pdf) |
| Dunedin CC | 2023/24, 2024/25 | **276 L/p/d (2023/24)**, **269 L/p/d (2024/25)** per resident (target <240; "not achieved") | **15% (2023/24)**, **9% (2024/25)** real water loss (non-revenue-water basis; target ≤20%) | **0% domestic** (all unmetered, fixed-rate charging) | 48,033 water connections (30 Jun 2024); pop 115,357 (4 schemes); serviced 116,058 | [DCC WSDP 2025](https://www.dunedin.govt.nz/__data/assets/pdf_file/0018/1265112/Water-Services-Delivery-Plan.pdf); [DCC 9YP 2025-34 p.170](https://www.dunedin.govt.nz/__data/assets/pdf_file/0005/1143473/9-Year-Plan-2025-34.pdf) |
| Invercargill CC | 2022/23 baseline; 2024/25 Q3 | **231 L/day (2022/23 baseline)**, **209.9 L/day (2024/25 Q3 YTD)** (target <300) | **18.5% (2022/23 baseline)** (target <30%; AMP: "just below 20%") | No universal metering (area meters 2025/26–2028/29; universal planned 2033/34); high-use non-res metered | 57,100 pop (2023); 21,760 conns (20,360 res + 1,400 non-res) | [ICC LTP 2024-34](https://www.icc.govt.nz/repository/libraries/id:2swc6cbtp1cxby8vraxn/hierarchy/assets/council/documents/plans-and-reports/long-term-plan/2024-2034-LTP-Proper-Full-document.pdf) p.80; [ICC 3Ws AMP 2024](https://www.icc.govt.nz/repository/libraries/id:2swc6cbtp1cxby8vraxn/hierarchy/assets/council/documents/asset-management-plans/Three-Waters-Asset-Management-Plan-A5424593.pdf); [ICC Perf Q3 2025](https://www.icc.govt.nz/repository/libraries/id:2swc6cbtp1cxby8vraxn/hierarchy/assets/council/council-performance/performance-reports/2024-2025/2025%2005%2020%20ICC%20Performance%20report%20Q3%202025%20%28A5891179%29.pdf) |
| Napier CC | 2024/25 (AR) | **436 L/p/d** per resident (2022/23: **361** — this is the "~360 L/p/d" figure from the brief; 2023/24: 394) | **18%** real loss (2022/23: 14.8%; 2023/24: 19.1%) | 6.9% of connections metered (804 res + 923 non-res of 24,997) | 62,992; 24,997 conns | [Napier AR 2024/25](https://www.napier.govt.nz/assets/Document-Library/Reports/Annual-Reports/NCC-AnnualReport2025-Web.pdf) p.25; [Napier AR 2022/23](https://www.napier.govt.nz/assets/Document-Library/Reports/Annual-Reports/NCC-Annual-Report-2022-23-Spread-Version.pdf) p.25 |
| Hastings DC | 2024/25 (AR) | **666 L/p/d** per resident (2023/24: 663) | **22.6%** real loss (2023/24: 18.9%) | 16.1% of connections metered (3,025 res + 947 non-res of 24,599) + ~2,000-property smart-meter trial | 69,959 district (65,026 urban); 24,599 conns | [Hastings AR 2024/25](https://www.hastingsdc.govt.nz/assets/Document-Library/Reports/Annual-Report/2024-2025-Annual-Report-web-version.pdf) pp.19–20 |
| Hamilton CC | 2024/25 (AR) | **321 L/p/d** per resident (2023/24: 323; target ≤400) | **14.9%** real loss (2023/24: 11.6% ±31% CI; Apr 2024–Mar 2025 ±23% CI) | Res meters not reported; non-res 62.8% (3,449 of 5,490); "most water use unmetered at point of supply" | 192,000; 65,083 conns | [Hamilton AR 2024/25](https://hamilton.govt.nz/assets/Uploads/Documents/2024-2025-Annual-Report-V25-Digital-F.pdf) pp.156, 160 |

> **Note on the brief's "~360 L/person/day":** no published Hastings figure near 360 exists — that figure is
> **Napier's 361 L/p/d (2022/23)**. Hastings' published per-capita consumption is 663–666 L/p/d (council
> DIA measure) and ≈672–682 L/p/d (NEPR-derived). All Hawke's Bay urban supplies are unmetered, which
> drives very high use (RNZ, 4 Aug 2026: Hastings CARL 436 L/conn/day ≈ 10.0M L/day lost;
> Napier 197 ≈ 5.5M L/day — https://www.rnz.co.nz/news/regions/884218/leaks-waste-more-than-15-million-litres-of-water-a-day-in-hawke-s-bay).

---

## (c) Caveats

1. **The Water NZ NPR ended at 2021/22.** Do not look for an "NPR 2022/23 or newer" from Water NZ —
   none exists. From 2023 the successor is Taumata Arowai's NEPR (2022/23, 2023/24, 2024/25). For
   the dashboard, the **NEPR 2024/25 (published June 2026) is the latest available**.
2. **Figures are for territorial authorities/CCOs, not regional councils.** Water is delivered by the
   suppliers listed; regional councils (Auckland Council as regional council, ECan, ORC, HBRC, ES, WRC)
   do not operate the urban networks (Auckland Council's own NEPR entries are tiny regional-park supplies).
3. **Year alignment across suppliers:** Table 1 is a single reporting year (2024/25) for all suppliers.
   In Table 2 (NPR), Auckland (Watercare) and Hastings did not submit for the final NPR 2021/22 —
   their latest NPR row is **2020/21** (noted per row).
4. **Metric-name mismatch between eras:** NPR reported "Average Daily Residential Water Consumption
   (L/connection/day)" (`WSB8`) and "% estimated total network water loss" (`WSE1b`); the NEPR reports
   "Median residential water consumption (L/connection/day)" (`D-RE4`) and raw loss volumes (`D-RE1`)
   plus CARL/UARL/ILI. The L/person/day column is **derived** (= supply ÷ population ÷ 365 × 1000) in
   both tables, so it is comparable across eras; the %-loss is only directly published for NPR years
   ≤2020/21 (for 2021/22 and NEPR years it is computed from reported loss volume ÷ supply volume).
5. **Data-quality flags (as published):** Dunedin's D-RE4 (677 L/conn/day) is flagged "1 – Very
   Uncertain"; Hamilton's is "3 – Less Reliable"; Hastings/Napier "3 – Less Reliable"; Invercargill
   WSB8 for NPR 2021/22 is negative (−825.6, non-residential use reported > total supply). Christchurch
   did not report total supply (`WSB5`) for NPR 2021/22.
6. **Metering %:** Auckland (Watercare) 100% metered — confirmed across all sources. Christchurch
   reports ~92–94% residential metering in both NPR 2021/22 and NEPR 2024/25 (the NEPR 2024/25 report
   Table 5 lists Christchurch at 94%); note this counts meter installations — Christchurch does not
   charge volumetrically. Hamilton did not report residential metering in NEPR 2024/25 (blank).
7. **Small-supply noise:** Selwyn/Waimakariri/Hastings figures are aggregates across many small
   networks; ILI and per-connection metrics vary strongly between networks (e.g. Selwyn ILI 0.9–8.3;
   Waimakariri CARL 0.4–6.2 L/conn/day depending on network). Use main-network or aggregated values
   with care.
8. The NEPR explicitly cautions that **% water loss is not directly comparable across operators**
   (different estimation methods, especially in unmetered networks).
9. **L/person/day bases differ (Tables 1/2 vs Table 4):** Table 1/2 L/person/day = *water supplied per
   capita* (supply ÷ population ÷ 365). Table 4 figures are the suppliers' own published measures:
   most councils publish *consumption per resident* (DIA measure 5), which excludes network losses and
   non-residential use — e.g. Christchurch 239 L/resident/day (DIA) vs 367 L/person/day (supply-based);
   Watercare 257 L/person/day (gross, incl. commercial) vs 269 (supply-based). Never mix the two bases
   in one analysis.
10. **Leakage bases differ:** council "real water loss %" (DIA measure 2 / water balance) ≠ NEPR
    "total drinking water loss" (D-RE1) ≠ CARL L/connection/day. Example: Watercare reports 12.8%
    network loss (AR 2025) while NEPR 2024/25 D-RE1 implies 19.7% — different scopes (e.g. whether
    private-side loss and unmetered estimates are included). Report the exact metric name with every
    number.
11. **NEPR 2023/24 water-loss values are low-confidence** (Taumata's own external review found 50% of
    operators corrected their loss data; e.g. Selwyn & Waimakariri show 35 L/conn/day CARL in 2023/24
    vs 153/230 in 2024/25 — a methodology/data change, not a real 7× increase). Prefer 2024/25 values.
12. **NPR 2021/22 data gap:** Water NZ's final NPR report PDF was archived as a definitions/mapping
    document; the participant-level data lives in the public Tableau dashboard (extracted here).
    Auckland (Watercare) and Hastings did not submit 2021/22 rows — their latest NPR row is 2020/21.
13. **Waimakariri & Christchurch figures:** Waimakariri's 319/260 L/p/d is a 2025 planning estimate
    (not measured); Christchurch was absent from NEPR 2023/24 supply/loss figures (did not report) —
    its NEPR 2024/25 and CCC AR 2025 figures are used instead.

---

## (d) Licence / terms

- **Water New Zealand NPR data:** the NPR **dashboard data is public** on waternz.org.nz (no login).
  The NPR **report PDFs are members-only** (login wall, confirmed 2026-08-30). Water NZ's standard
  copyright statement (as printed in its publications; the NPR copyright page is behind the login, so
  the exact NPR wording could not be read directly):
  > "Copyright © Water New Zealand. Reproduction, adaptation or issuing of this publication for
  > educational or other non-commercial purposes is authorised without prior permission of Water New
  > Zealand. Reproduction, adaptation or issuing of this publication for resale or other commercial
  > purposes is prohibited without the prior permission of Water New Zealand." (permission:
  > enquiries@waternz.org.nz)
  Attribution to Water New Zealand required when reusing.
- **Taumata Arowai NEPR reports:** explicit statement in both the 2023/24 and 2024/25 reports:
  > "Unless otherwise stated, the information in this Network Environmental Performance Report is
  > protected by copyright and is subject to the copyright laws of New Zealand. The information may be
  > reproduced without permission, subject to the material being reproduced accurately and not being
  > used in a misleading context. In all cases, the Water Services Authority – Taumata Arowai must be
  > acknowledged as the source."
- **NEPR 2024/25 unit-level data on data.govt.nz:** licensed **Creative Commons Attribution 3.0 New
  Zealand (CC BY 3.0 NZ)** — free to reuse with attribution.
- **Recommendation for this project:** use the NEPR 2024/25 data extract (CC BY 3.0 NZ) as the primary
  source, attribute Taumata Arowai, and use the final NPR 2021/22 dashboard data (Water NZ) for the
  historical comparison with attribution to Water New Zealand.

---

## Appendix A — method (how the numbers were obtained)

1. **NPR 2021/22 (and 2013/14–2020/21):** downloaded the public Tableau workbook
   `https://public.tableau.com/workbooks/ResourceEStory2022.twb` (Water NZ "Resource Efficiency" NPR
   dashboard), unzipped `federated.hyper`, read the `Extract` table with Tableau Hyper API, and
   extracted the drinking-water measures (WSB1a–WSB8, WSA9a/b, WSE1a–h, WSA1a) for all 64+ participants
   × 9 years. Participant names in the data are short forms (e.g. "Auckland", "Christchurch",
   "Dunedin") — mapped to full names in this report.
2. **NEPR 2024/25:** downloaded the unit-level CSV extract from data.govt.nz
   (`nepm-2024-2025-csv-files.zip`) and the NEPR 2024/25 PDF; aggregated DW_Network rows per
   organisation (sum of supply/loss/CARL/UARL, population and connections) and took main-network values
   for D-RE4/ILI. Derived L/person/day = `D-EH4`×1000/365/`D-EH3`; loss % = `D-RE1`/`D-EH4`;
   CARL per connection/day = `D-RE2.1`×1000/365/(res+non-res connections).
3. **NEPR 2023/24:** extracted text from the public PDF; per-council Figures 29–31 read with
   coordinate-based text extraction (pdfplumber) to pair labels with values.
4. Cross-checks: Water NZ press releases (Story 1939/1940), Scoop (2022 NPR release), Newsroom five
   charts, Hastings DC news item, Taumata Arowai insights page. National aggregates in press releases
   (e.g. 213,000 L/property/yr; 281.8 L/person/day) are quoted verbatim — note they may use a slightly
   different participant set/computation than the raw extract.
