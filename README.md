# NZ Water × Population

> **Temporary public demo, 26 October 2026:** the live URL displays a frozen
> historical release matching the portfolio screenshots while the revised design
> is developed. Its earlier estimates are under review. Current audited code stays
> in this repository; the bilingual/climate work stays on `frontend/overview-preview`.
> [Publication status and how to resume](docs/PUBLIC-RELEASE.md).

[![pipeline](https://github.com/LuciaLXH/nz-data-dashboard/actions/workflows/refresh.yml/badge.svg)](https://github.com/LuciaLXH/nz-data-dashboard/actions)
[![data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-1c6b67)](#data-sources--licences)

**How do population growth, network supply and water loss compare across six NZ regions?**

[**Live site →**](https://lucialxh.github.io/nz-data-dashboard/) · [The SQL →](sql/) · [Analysis →](ANALYSIS.md)

> **Local revision: water, population and seasonal-flow schema v2 implemented.** Identity conflicts
> are quarantined, supply/person uses matched records, and loss rates use total
> loss divided by total supply within the same reporting boundary. Coverage and
> actual years accompany the results. This local revision has not been deployed;
> the live site can still show the previous release.

[Data dictionary](docs/DATA-DICTIONARY.md) ·
[Source audit and decisions](docs/SOURCE-AUDIT-2026-10-22.md) ·
[修改说明（中文）](docs/CHANGELOG.zh-CN.md) ·
[修改前后快照](docs/changes/README.md)

## What the dashboard helps you investigate

1. **Network supply per served person.** Differences can reflect customer mix,
   water losses, metering and reporting methods. They do not directly measure
   household consumption or achievable efficiency savings.
2. **Reported water loss and coverage.** Providers estimate losses, sometimes
   including private-side losses. Comparisons need consistent boundaries and
   the same networks in the numerator and denominator. The default cohort excludes private-side losses; included and unknown
   boundaries appear separately. An empty cohort is unavailable, never zero.
3. **Dated river observations.** The project integrates three HBRC telemetry
   sites and eight historical ORC sites. These selected observations do not
   establish region-wide availability, and a cached reading may be old.

The earlier savings comparison and investment-priority claims have been
withdrawn. Read [ANALYSIS.md](ANALYSIS.md) for the evidence boundaries and
conditions for publishing revised findings. The previous demo GIF is retained
as a historical asset and is no longer embedded as a current demonstration.

## Who this is for

**Audience:** analysts exploring public water-network and population data.
**Use:** identify differences and data gaps that warrant further investigation.
Select a region, inspect the measure, then check dates, coverage and assumptions.

Scope: **six regions** — Auckland · Canterbury · Otago · Hawke's Bay · Southland ·
Waikato. Networks are grouped by operator; this does not verify each network's
service area against regional boundaries. The project cannot rank supply-zone
shortages or investment options without capacity, climate, allocation and cost
evidence. Water-quality and land-use analysis is deferred.

## How it works

```
Stats NZ ADE API ─┐
Taumata NEPR ────┼─→ scripts/  ─→ DuckDB ─→ data/processed/*.json ─→ static site
Council Hilltop ──┤     (extract)   (sql/)     + schema + _runs.jsonl    (ECharts
LAWA snapshot ────┘                                                     + Leaflet)
```

- `data/processed/` is the **single source of truth** for the front end:
  versioned JSON + JSON Schema + a UTC timestamp per source.
- In normal publication mode, the pipeline runs every six hours. During the temporary
  historical-demo period, scheduled runs republish the frozen snapshot without fetching new data.
  Source release/observation dates differ
  from refresh time; source-specific fetching and freshness rules remain pending.
- The site's **Data Health** panel reads `_runs.jsonl`: last successful run,
  row counts, null rates, schema version, last 20 runs.

## The SQL

Python prepares source records; DuckDB runs the analytical SQL in `sql/`.
Python preserves source records and exclusions; validation reconciles the SQL
outputs to per-network contributions. See the data dictionary for each denominator.

| File | What it does |
|---|---|
| [`01_region_population_growth.sql`](sql/01_region_population_growth.sql) | YoY + 5-year CAGR per region using actual calendar years; missing years suppress growth measures |
| [`02_supply_per_capita.sql`](sql/02_supply_per_capita.sql) | Reported network supply, matched supply/person, boundary-specific loss rates and coverage; separate population scenarios with explicit years |
| [`03_flow_percentile.sql`](sql/03_flow_percentile.sql) | Latest observed river flow vs calendar-centred completed prior seasons; ranks require ≥3 seasons with ≥10 days each, with per-season coverage (11 curated sites) |

## Why I don't claim causation

- **Ecological fallacy** — council-level correlation says nothing about
  catchment-level mechanism.
- **n = 6** — no correlation across this few units is robust; one large
  council can flip the sign.
- **Confounding** — customer mix, metering, geography and reporting methods can
  affect water comparisons. Their individual effects have not been isolated.
  Water-quality and land-use analysis is deferred.
- **Site selection bias** — LAWA monitoring sites are not randomly located.
- NEPR/NPR figures are council-reported; metering coverage varies.
- Optional regional supply scenarios include residents outside reporting
  networks; no regional loss scenario is inferred. Reported values may also be
  estimates, and network-input sums may double count transfers.

## Data sources & licences

| Source | Used for | Cadence | Licence |
|---|---|---|---|
| [Stats NZ SDMX API](https://explore.data.stats.govt.nz/) | Subnational population estimates (series starts 2018, 6 regions) | Annual (30 Jun) | CC BY 4.0 |
| [Taumata Arowai NEPR](https://www.taumataarowai.govt.nz/) | Network supply, estimated water loss and reporting context (NPR successor) | Annual | CC BY 3.0 NZ |
| [Water New Zealand NPR 2021/22](https://www.waternz.org.nz/NationalPerformanceReview) | Historical research/reference material; not the current sql/02 input | Ended 2021/22 | Water NZ terms (non-commercial with attribution) |
| [LAWA](https://www.lawa.org.nz/explore-data/water-quantity/) | Regional council boundaries (WKT via LAWA map service, derived from Stats NZ) | Static | CC BY 4.0 |
| HBRC Hilltop (`data.hbrc.govt.nz`) | River flow, realtime (3 sites) | 15 min | Per-council terms; public access |
| ORC Hilltop (`gisdata.orc.govt.nz`) | River flow, historical 2010–2021 (8 sites) | 5 min | Per-council terms; public access |
| [LAWA](https://www.lawa.org.nz/download-data) | River water quality state & trend | Annual snapshot, downloaded 2026-08-30 | CC BY 4.0 |

Contains data sourced from Stats NZ and licensed for reuse under **CC BY 4.0**.
Water quality data courtesy of **LAWA** and New Zealand's regional councils.
Boundary data via **LAWA** (CC BY 4.0; originally derived from Stats NZ regional
council boundaries). Water demand/network data courtesy of **Taumata Arowai**
(CC BY 3.0 NZ) and **Water New Zealand**. River flow data courtesy of
**Hawke's Bay Regional Council** and **Otago Regional Council** public Hilltop servers.

## Run it yourself

Install the dependencies once, then build and test the attributed examples:

```bash
git clone https://github.com/LuciaLXH/nz-data-dashboard && cd nz-data-dashboard
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
make offline                # real transform → schemas → reconciliation → example site
make test                   # creates fresh example outputs; no API key or raw cache
make serve-offline          # http://localhost:8001
```

Examples are small source excerpts, **not representative regional totals**.
Their [manifest](fixtures/offline/MANIFEST.json) records attribution, selection,
hashes and original record numbers. The example site is isolated in `.tmp/offline/`
and displays an explicit banner. Data builds/tests make no network requests;
browser libraries, map tiles and external links still need internet access.

For a production refresh:

```bash
cp .env.example .env        # add your Stats NZ API key
set -a; source .env; set +a
make all                    # fetch → transform → validate → package production site
DASHBOARD_PROCESSED_DIR=data/processed make test
make serve                  # http://localhost:8000
```

For an existing local raw snapshot, run `scripts/transform.py`, then
`scripts/validate.py` with the project Python and `make site-data`; these do not
fetch new observations. Missing outputs fail checks rather than skipping them.
`make test` defaults to fresh fixtures; the refresh workflow explicitly tests its
production outputs. `offline-checks` also runs on pull requests without secrets.

`python3 scripts/audit_nepr.py` reproduces the dated stage-one input diagnostic
using only the standard library. The v2 loader shares its identity-handling rules.

## Repo layout

```
scripts/    extract + orchestrate (Python)
sql/        all business logic (DuckDB)
schemas/    JSON Schema per processed dataset
site/       static front end (ECharts + Leaflet), no build step
tests/      pytest
fixtures/   attributed offline examples + manifest
data/
  raw/      source snapshots
  processed/ generated JSON + _runs.jsonl (schemas live in schemas/)
```

## Status

Pipeline runs on GitHub Actions every 6 h plus a monthly trigger. Each run
currently fetches both flow and population; NEPR, LAWA and other reference
snapshots require manual updates. The workflow fetches → transforms → validates and tests (schemas, units, region names, DST boundaries,
missing-value propagation, percentiles, and fetch fallback) → builds `site/` → deploys to GitHub Pages via
`actions/deploy-pages` (generated data is deployed as a build artifact; the attributed NEPR
reference CSVs are retained in Git). If the badge above is red or the site footer says
*pipeline paused*, the data shown is the last good snapshot — the site
degrades to stale rather than blank, by design. Times are stored in UTC and
displayed in Pacific/Auckland on the site.

Build and deployment run as separate jobs. If Pages returns a transient
server error after the build succeeds, use **Re-run failed jobs** within the
artifact's 7-day retention window to retry deployment without refetching.
Validation history is cached between successful builds; cache eviction can
reset it. These bars describe data validation, not deployment status.

Review and repair record: [2026-10-10 project review](docs/REVIEW-2026-10-10.md).
Project motivation and planned improvements: [roadmap](docs/PLAN.md).

---

Built by Xiaohan (Lucia) Liu · Master of Applied Data Science,
University of Canterbury · [LinkedIn](https://linkedin.com/in/xiaohan-liu-755017382)
