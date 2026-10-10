# Project roadmap

Updated: 2026-10-10. This roadmap separates delivered functionality from
remaining analytical and engineering work.

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
