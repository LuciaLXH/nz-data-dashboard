# Project roadmap

Updated: 2026-10-24. This roadmap separates delivered functionality from
remaining analytical and engineering work.

## Project motivation

I started this project because of concerns about drought and water availability
in New Zealand. El Niño can increase the risk of dry conditions in some regions,
which led me to ask how population growth and water losses might add to pressure
on water supplies. I brought together public population, water-network and
river-flow data to explore these questions across six regions. The dashboard
compares demand-side pressures and available observations; it does not forecast
drought.

### Climate context

El Niño changes the likelihood of regional weather patterns rather than causing
uniform drought across New Zealand. Earth Sciences New Zealand's outlook issued
on 1 October 2026 reported very strong El Niño conditions, with reduced rainfall
favoured in the north and east of the North Island and increased rainfall favoured
in the west of the South Island. These are seasonal probabilities, not a claim
that drought has already occurred everywhere.
[October–December 2026 outlook](https://niwa.co.nz/climate-and-weather/seasonal-climate-outlook/seasonal-climate-outlook-october-december-2026).

The recent sequence was not two uninterrupted years of strong El Niño. The
2023–2024 event weakened in early 2024, with neutral conditions prevailing from
June through December 2024. Most of 2025 was neutral before a transition to
La Niña in October.
[2024 climate summary](https://niwa.co.nz/climate-and-weather/annual/annual-climate-summary-2024),
[2025 climate summary](https://niwa.co.nz/sites/default/files/2026-01/2025_Annual_Climate_Summary_ESNZ-web.pdf).

Climate risk provides the motivation for the project. The current pipeline does
not include ENSO indices, rainfall, soil moisture, or a complete supply-capacity
model, so it cannot attribute observed conditions to El Niño or predict water
shortages. This distinction should remain clear when the motivation is added to
the README and dashboard.

## Frontend preview — 2026-10-24

The validated baseline `533b527` has been pushed to main. Its GitHub Actions
release status must be checked separately from the push. The first frontend
preview lives on `frontend/overview-preview`: three compact overview entry points,
explicit action labels and a scope/date/missing-value reading guide. Metric
calculations and served data are unchanged. Paired desktop/mobile screenshots
are recorded in [the visual change log](changes/2026-10-24/README.md).
Review this local preview before extending the design to navigation and charts.

## Current iteration

The wording patch, source audit and v2 metric implementation are complete locally.
The frontend, schemas, data dictionary and offline examples use the same rules.
Deployment and the next analytical iteration remain separate.

| Stage | Status | Delivered result or completion criteria |
|---|---|---|
| Wording patch | Implemented | Withdraw unsupported savings/investment claims and old demo embeds; align the project question. |
| 1. Source and metric review | Complete | Record identity, private-loss boundaries, missingness, mapping and transfer evidence; publish the dictionary and diagnostic. |
| 2. Implement and validate metrics | Complete locally | Shared identity rules, source/quality references, reported totals, matched supply/person and boundary-specific loss rates with coverage; actual years through SQL/schema/UI. CARL/ILI remain unaggregated pending denominator research. |
| 2. Reproducible offline build | Complete locally | Attributed excerpts use the real pipeline; build/tests need no API key or raw cache after dependency installation. Core checks fail rather than skip missing outputs. Separate example banner, output folder and pull-request CI. |
| 3. Publish revised findings | Local presentation checked; release pending | Snapshot table reconciled; desktop/mobile checked; publish the revised release and replace historical demonstration assets when a new demonstration is prepared. No restoration of the savings claim. |

The project question is:

> How do population growth, network supply and water loss compare across six NZ regions?

Use the dashboard to identify questions for investigation. It does not rank
supply-zone shortages or investment options. Reported values take priority over
whole-region scenarios; the latter remain optional and require explicit assumptions.

- [Plain-language change record in Chinese](CHANGELOG.zh-CN.md)
- [Data dictionary and implementation status](DATA-DICTIONARY.md)
- [Source audit and handling decisions](SOURCE-AUDIT-2026-10-22.md)

## Later work

| Priority | Improvement | Completion criteria |
|---|---|---|
| Complete locally, 2026-10-23 | Seasonal percentiles and history sufficiency | Calendar windows cross New Year, Feb 29 has an explicit convention, current partial seasons are excluded, and per-season coverage controls whether a rank is shown. Before/after evidence is retained. |
| After the core metric release | User path and source dates | Make region → measure → coverage/assumptions easy to follow; distinguish observation, fetch and build dates and historical ORC records from HBRC telemetry. |
| After a usable revision | User feedback | Record actual misunderstandings and resulting changes; do not imply water-sector validation before it occurs. |
| Deferred | Water quality, land use, new integrations and Power BI | Reassess their value after the existing measures are reproducible and interpretable. |

## Delivered

- Public static dashboard hosted on GitHub Pages, with charts and a regional map.
- Stats NZ population estimates for six regions, NEPR 2024/25 network data,
  and river-flow observations from three HBRC and eight ORC sites.
- DuckDB SQL for population growth, regional supply scenarios, and flow percentiles.
- JSON Schema validation, offline regression tests, and a Data Health panel.
- Scheduled refreshes every six hours, cached source snapshots, per-site fallback,
  and explicit warnings when a source is degraded.
- Separate build and deployment jobs, unique Pages artifacts, and migration from
  the previous raw-snapshot cache format.
- Mobile layout checks and labels for scenarios and historical observations.
- A source audit, v2 metric dictionary and independent contribution reconciliation.
- Calendar-based seasonal flow comparisons, independent daily-source reconciliation and explicit history coverage.
- Attributed offline examples, schema v2 water/population outputs and coverage tables.

The [2026-10-10 review](REVIEW-2026-10-10.md) records the deployment incident,
repairs, verification results, and remaining limitations.

## Analytical priorities

- Maintain the applied identity decisions and reconcile each new source release before adoption.
- Distinguish supply, estimated total water loss, physical loss and residential consumption.
- Calculate aggregate loss rates on the same valid networks and reporting boundary;
  publish unavailable rather than zero when the comparable cohort is empty.
- Publish metric-specific coverage and exclusions; retain operator grouping as an
  explicitly approximate geography until service areas can be verified.
- Check transfers before interpreting network-input sums as unique regional volumes.
- Preserve explicit base/projection years and annual-continuity checks when adopting new population releases.
- Keep achievable savings, capacity headroom and costs outside the findings unless
  supporting evidence is added.

## Engineering priorities

- Fetch recent HBRC observations incrementally and reuse unchanged ORC history.
- Distinguish source year, latest observation, fetch time, and build time in the UI.
- Define freshness thresholds appropriate to each source and the refresh schedule.
- Keep attributed offline fixtures synchronized with versioned contracts; never present their sample totals as findings.
- Review action-runtime upgrades against official release notes and Linux CI.

## Documentation and data maintenance

- Maintain English technical documentation, source attribution, and dated limitations.
- Before each logical change, capture the affected page and its data under
  `docs/changes/<date>/<step>/before/`; after validation, capture `after/` using the
  same input snapshots, calculation date, section and viewport. Do not overwrite
  evidence or manufacture missing before images. Explain changes in plain Chinese.
  See the [snapshot workflow](changes/README.md) and `scripts/capture_change.py`.
- Record each substantive adjustment in `CHANGELOG.zh-CN.md`: what changed, why,
  what readers should do differently, and what remains pending. Update the data
  dictionary whenever a source, metric definition or reporting boundary changes.
- Update NEPR and LAWA reference snapshots manually when new releases are adopted.
- Keep personal interview notes, career preparation, and local tool logs outside
  version control.
