# NZ Water × Population

[![pipeline](https://github.com/USER/REPO/actions/workflows/refresh.yml/badge.svg)](https://github.com/USER/REPO/actions)
[![data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-1c6b67)](#data-sources--licences)

**Where will population growth put NZ council water supplies under pressure first?**

[**Live site →**](https://USER.github.io/REPO/) · [The SQL →](sql/) · [Findings →](ANALYSIS.md)

![demo](docs/demo.gif)

---

## TL;DR — three findings

1. **[Number].** [One sentence of evidence.]
   *So what:* [what a council planner should do differently.]
   ![](docs/fig1.png)

2. **[Number].** [Evidence.]
   *So what:* [decision implication.]

3. **[Number].** [Evidence.]
   *So what:* [decision implication.]

> Full write-up, method and caveats: [ANALYSIS.md](ANALYSIS.md)

## Who this is for

**Audience:** regional council asset planners and three-waters analysts.
**Decision it supports:** which supply zones are most likely to face a
demand–supply gap under projected population growth over the next 5 years.

Every chart on the site answers one sub-question of that decision.
Scope: [N] councils — [list]. Depth over national coverage, deliberately.

## How it works

```
Stats NZ ADE API ─┐
Water NZ NPR ─────┼─→ scripts/  ─→ DuckDB ─→ data/processed/*.json ─→ static site
Council Hilltop ──┤     (extract)   (sql/)     + schema + _runs.jsonl    (ECharts
LAWA snapshot ────┘                                                     + Leaflet)
```

- `data/processed/` is the **single source of truth** for the front end:
  versioned JSON + JSON Schema + a UTC timestamp per source.
- Refresh cadence matches each source's real cadence — see the table below.
  This is an **automated pipeline with freshness SLAs**, not a real-time feed.
- The site's **Data Health** panel reads `_runs.jsonl`: last successful run,
  row counts, null rates, schema version, last 20 runs.

## The SQL

All business logic lives in `sql/`; Python only does IO and orchestration.

| File | What it does |
|---|---|
| [`01_region_population_growth.sql`](sql/01_region_population_growth.sql) | YoY + 5-year CAGR per council (window functions) |
| [`02_supply_per_capita.sql`](sql/02_supply_per_capita.sql) | Joins population to Water NZ NPR; litres/person/day, leakage, metering |
| [`03_flow_percentile.sql`](sql/03_flow_percentile.sql) | Current river flow vs same-week historical percentile |

## Limitations & why I don't claim causation

- **Ecological fallacy** — council-level correlation says nothing about
  catchment-level mechanism.
- **n = [N]** — no correlation across this few units is robust; one large
  council can flip the sign.
- **Confounding** — land use (dairy intensity, irrigation) drives NZ river
  water quality far more than urban population. Section [B] shows the
  population signal weakens once land use is accounted for.
- **Site selection bias** — LAWA monitoring sites are not randomly located.
- Water NZ NPR is self-reported by councils; metering coverage varies.

## Data sources & licences

| Source | Used for | Cadence | Licence |
|---|---|---|---|
| [Stats NZ — Aotearoa Data Explorer](https://portal.apis.stats.govt.nz/) | Subnational population estimates | Annual (30 Jun, released Oct) | CC BY 4.0 |
| [Stats NZ Geographic Data Service](https://datafinder.stats.govt.nz/) | Regional council boundaries | Static | CC BY 4.0 |
| [Water New Zealand NPR](https://www.waternz.org.nz/NationalPerformanceReview) | Litres/person/day, leakage, metering | Annual | See publisher terms |
| [council] Hilltop server | River flow / level | 15 min – 1 h | [per-council] |
| [LAWA](https://www.lawa.org.nz/download-data) | River water quality state & trend | Annual snapshot, downloaded [DATE] | CC BY 4.0 |

Contains data sourced from Stats NZ and licensed for reuse under **CC BY 4.0**.
Water quality data courtesy of **LAWA** and New Zealand's regional councils.
Boundary data © **Stats NZ / LINZ**, CC BY 4.0. Changes were made.

## Run it yourself

```bash
git clone https://github.com/USER/REPO && cd REPO
cp .env.example .env        # add your Stats NZ API key
make all                    # fetch → transform → validate → build site
make test                   # pytest: schema, units, region names, DST, nulls
python -m http.server -d site 8000
```

`data/raw/sample/` holds a trimmed fixture set so `make test` runs offline.

## Repo layout

```
scripts/    extract + orchestrate (Python)
sql/        all business logic (DuckDB)
schemas/    JSON Schema per processed dataset
site/       static front end (ECharts + Leaflet), no build step
tests/      pytest
data/
  raw/      source snapshots + sample fixtures
  processed/ single source of truth: *.json, *.schema.json, _runs.jsonl
```

## Status

Pipeline runs on GitHub Actions: flow every 6 h, water quality and population
monthly. If the badge above is red or the site header says *pipeline paused*,
the data shown is the last good snapshot — the site degrades to stale rather
than blank, by design.

---

Built by [Feng Jiang](https://github.com/USER) · MADS (Distinction),
University of Canterbury · [LinkedIn](#)
