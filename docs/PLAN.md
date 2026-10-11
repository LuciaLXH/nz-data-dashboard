# Project roadmap

Updated: 2026-10-12. This roadmap separates delivered functionality from
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

## Next iteration

All items below are planned. The current dashboard remains unchanged.

| Priority | Improvement | Completion criteria |
|---|---|---|
| 1 | Align conclusions across the dashboard, README, analysis, and chart images | Remove unsupported claims about the cheapest intervention, fixing pipes before adding capacity, and years of growth headroom. Distinguish evidence from planning hypotheses everywhere. |
| 1 | Separate reported values from regional scenarios | Publish reported network supply and loss alongside population-based scenarios; expose coverage and missingness; calculate aggregate loss rates as total reported loss divided by total reported supply. Align the population basis of the existing 62% comparison before interpreting it. |
| 1 | Provide a reproducible offline example | Include small attributed fixtures and a documented build that needs no API key. Define dataset grain, join keys, and core metrics; ensure the example exercises relevant validation rather than skipping for missing data. |
| 2 | Match the project question to the analytical scope | Present comparisons across six regions as a way to identify further investigation needs. Avoid claiming to rank supply shortages or individual supply zones without capacity, climate, and allocation evidence. |
| 2 | Make the dashboard easier to use | Support a clear path from selecting a region to comparing metrics and checking dates, coverage, and assumptions. Place definitions beside charts and visibly distinguish historical ORC observations from recent HBRC telemetry. |
| 2 | Strengthen date and percentile handling | Carry base/projection years through SQL, schemas, and labels; correct and test seasonal windows at year boundaries and leap days. |
| 3 | Gather user feedback | Invite analysts or people with water-sector knowledge to try the dashboard. Record actual misunderstandings, resulting changes, and limitations; do not imply stakeholder validation before it occurs. |
| Optional | Add a Power BI example | If relevant to intended use, reuse validated SQL outputs in a small model with documented measures and relationships. Keep definitions consistent with the main dashboard. |

The first iteration should focus on the three priority-1 items before adding
new charts or data integrations. A possible revised question is:

> How do population growth, per-capita supply and reported water losses compare
> across six NZ regions?

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
- Mobile layout checks and clear labels for estimated volumes and source years.

The [2026-10-10 review](REVIEW-2026-10-10.md) records the deployment incident,
repairs, verification results, and remaining limitations.

## Analytical priorities

- Separate reported network totals from population-based regional scenarios.
- Align the population coverage used in efficiency and projected-growth comparisons.
- Aggregate loss rates using total reported loss divided by total reported supply.
- Carry explicit base and projection years through SQL, schemas, charts, and labels.
- Correct and test seasonal percentile windows around year boundaries and leap days.
- Assess efficiency scenarios against cost and recoverable-loss evidence before
  presenting them as investment recommendations.
- Complete the proposed water-quality and land-use analysis; it is currently pending.

## Engineering priorities

- Fetch recent HBRC observations incrementally and reuse unchanged ORC history.
- Distinguish source year, latest observation, fetch time, and build time in the UI.
- Define freshness thresholds appropriate to each source and the refresh schedule.
- Add small public-source fixtures for a reproducible offline build.
- Review action-runtime upgrades against official release notes and Linux CI.

## Documentation and data maintenance

- Maintain English technical documentation, source attribution, and dated limitations.
- Update NEPR and LAWA reference snapshots manually when new releases are adopted.
- Keep personal interview notes, career preparation, and local tool logs outside
  version control.
