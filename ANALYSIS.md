# Analysis & Findings

> **Status: W2 — findings finalised with real numbers (2026-08-30).**
> Main line A (demand-side supply pressure) is backed by 6/6-region data
> (Stats NZ population × NEPR 2024/25 unit-level network data). The flow
> layer (sql/03) is a **supporting, site-level layer**: 11 curated public
> sites in 2 of the 6 councils — see its caveats below. Section B (water
> quality) is outlined; analysis comes after the site is stable.

## The three findings

Each finding = **one number + one chart + one "so what"**. These land in the
README TL;DR and in the site's Key Findings block.

### Finding 1 — Per-capita use differs 2.3× across the 6 regions; growth is not the only lever
- **Evidence:** Hawke's Bay supplies **609.7 L/person/day** vs Auckland
  **269.7** (NEPR 2024/25, population-weighted across all registered supplies).
  If Hawke's Bay matched Auckland's per-capita use it would free ≈
  **48,800 m³/day — ~62% of the entire 6-region demand growth projected to
  2030** (+79,300 m³/day, +6.0% at 2025 per-capita rates).
- **Chart:** bubble chart (pop growth × litres/person/day, size = daily
  demand, colour = leakage).
- **So what:** before adding supply capacity, planners have a demand-side
  lever worth 1.5–2 years of regional growth: efficiency and metering.
  Auckland's 99.9%-metered network is the benchmark; the least-efficient
  regions (Hawke's Bay, Otago 511, Southland 536 L/p/d) have the most
  headroom.

### Finding 2 — Leaks lose a fifth of everything the 6 regions put into their networks
- **Evidence:** **298,671 m³/day (22.5% of daily supply)** is lost to leaks
  across the 6 regions. Canterbury alone leaks **86,832 m³/day — 3.5× its own
  projected 2030 demand growth** (+24,815 m³/day). The leaked volume would
  serve ≈ **1.1 million people** at Auckland's usage.
- **Chart:** demand-now-vs-2030 bars with leak volume overlay.
- **So what:** leakage is a supply-side lever that does not wait for
  population. A region can buy more growth headroom by fixing leaks than by
  building new capacity — Canterbury's leak volume already exceeds a decade
  of its projected growth.

### Finding 3 — Only 2 of 6 councils publish open river-flow time series
- **Evidence:** of the 6 project councils, only **HBRC (live) and ORC
  (historical, public server frozen 2021-04-23)** expose open flow time
  series; Canterbury/Southland/Auckland public endpoints expose metadata
  only, Waikato's is down. Where live data exists (3 Hawke's Bay sites,
  2026-08-30): Ngaruroro at Fernhill at the **9.5th percentile** of its
  5-year same-week record (driest ~10% of late-August flows), Mohaka 31.1th,
  Tukituki 40.5th.
- **So what:** source-water availability is only locally observable today.
  NZ's water decisions lean on fragmented public data — demand-side planning
  must rely on 6/6 datasets like NEPR, and flow/availability needs the
  W1.5 follow-up (LAWA water-quantity API / ORC AQWebPortal) to be
  comparable across councils.

---

## Section B — Can population growth explain regional water quality?

**Claim to test:** population growth does **not** explain NZ river water
quality once land use is accounted for.

- **Approach:** partial correlation / stratification — correlate population
  growth vs LAWA water-quality metrics, then control for land use (dairy
  intensity, irrigation area per council).
- **Method note:** this mirrors the analytical approach used in my PHF
  Science internship (flood-disturbance effects on water quality). **Method
  reused; data entirely from public LAWA snapshots. No PHF data or
  unpublished results appear in this repository.**
- **Status:** LAWA snapshots (7 files) landed 2026-08-30; land-cover +
  river-quality join and the stratified correlation are **pending** (after
  the W2 site is accepted).

## Method

| Step | SQL | Data | Coverage |
|---|---|---|---|
| Population growth (YoY, 5-yr CAGR) | `sql/01` | Stats NZ SDMX API, 2018–2025 | 6/6 regions |
| Demand-side pressure: per-capita supply, leakage, CARL, ILI, implied daily demand + 2030 projection | `sql/02` | NEPR 2024/25 unit-level (all registered supplies) | 6/6 regions |
| Source availability: latest flow vs same-week historical percentile | `sql/03` | HBRC + ORC public Hilltop servers | 2/6 councils, curated sites |
| Water consents: share of consented volume by use (context layer, not SQL) | — | LAWA water-quantity API (`waterusage`, CC BY 4.0) → `data/ref/water_consents.json` | 5/6 regions (Otago: no data published) |

All business logic lives in `sql/` and runs via DuckDB; Python only does IO.
The consents layer is a **context layer**: it shows where each region's water is
*allocated* (consent = authorised take, not actual use) — Canterbury allocates
82% of consented volume to irrigation, Auckland 63% to drinking water.

## Limitations

- **Ecological fallacy** — council-level correlation says nothing about
  catchment-level mechanism.
- **n = 6** — no correlation across this few units is robust; one large
  council can flip the sign.
- **Confounding** — land use (dairy intensity, irrigation) drives NZ river
  water quality far more than urban population.
- **Site selection bias** — LAWA monitoring sites are not randomly located.
- **NEPR is council-reported** — self-reported network data; metering
  coverage varies; not every supply reports every metric (nulls excluded
  from weighted averages).
- **Flow layer is a curated sample** — 11 sites, 2 councils, not the full
  network; ORC circles show the last observation of the public record
  (frozen 2021-04-23), **not** current conditions. Current ORC flows are
  published on ORC's AQWebPortal and LAWA — outside this pipeline's scope
  so far (W1.5).
- **Projection is demand-only** — "2030 demand" multiplies today's per-capita
  use by projected population; it is not a full supply–demand model
  (consents, network capacity, climate).
- **Consents ≠ use** — the LAWA consent chart shows authorised volume, not
  actual takes; Otago publishes no consent-use data on LAWA.
