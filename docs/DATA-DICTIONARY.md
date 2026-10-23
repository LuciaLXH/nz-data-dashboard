# Data dictionary

Updated: 2026-10-23. Water, network contributions, population-growth and seasonal-flow outputs
now use **schema v2** in the local implementation. The rules below are executable
and reconciled to source contributions. Deployment is separate. See the
[source audit](SOURCE-AUDIT-2026-10-22.md) and [Chinese change record](CHANGELOG.zh-CN.md).

## Reading the measures

- **Reported（上报）** describes where a value came from. A provider may have
  estimated it; reported does not mean independently measured or verified.
- **Derived（计算所得）** combines reported values using a stated calculation.
- **Scenario（情景估算）** asks what would happen under explicit assumptions.
  It does not predict a shortage or establish achievable savings.
- **Missing（缺失）** means unknown, not zero. A missing result is shown as
  unavailable, never silently replaced by a zero or a neighbouring network.
- **Coverage（覆盖范围）** must say what is covered: networks, reported supply
  volume, or population. Those are different denominators.

## Dataset grain and joins

| Dataset | What one record represents | Key and join rule | Time and geography |
|---|---|---|---|
| NEPR `DW_Network.csv` | A source record describing a network; repeats and ID conflicts exist | Retain source filename, release and CSV record number. Candidate analytical key: release + `Account ID` + `Supply ID`; require consistent organization/name and reviewed values before combining repeats. Do not join by display name alone. | 2024/25 reporting period; 2026-07-27 extract. Network service areas are not provided by the project's organization mapping. |
| NEPR `DW_Org.csv` | Organization-level measures, including imports, exports and metered connection counts | Candidate key: release + `Account ID`; validate uniqueness before joining. Organization totals must not be repeated and summed across its networks. | Same release as the network extract. |
| Population | Estimated residents in one region in one year | `region` + `year`, unique; join explicitly to the selected population year | Stats NZ ERP at 30 June; geographic regions, not network customers. |
| Population growth | Change for one region and year | `region` + `year`; compare actual year offsets, not merely previous rows | Actual calendar-year joins; CAGR requires all six annual observations in the five-year interval. |
| Flow observations | One council, monitoring site and observation date after daily aggregation | `council` + `site` + `date`; check uniqueness and unit consistency before percentile calculation | Site geography; not a region's available drinking-water capacity. |
| Flow percentile | Latest available observation and its historical comparison for one site | `council` + `site`; join coordinates using both fields | Latest observation date differs from fetch/build date. ORC records used here are historical. |
| Region reference and boundaries | One project region, its labels and map shape | Stable project `region` key; display names are labels | Six regions; neither six operators nor six supply zones. |
| Water consents | A region's snapshot of authorised volumes by use category | `region` + category; not joined to network supply as consumption | LAWA snapshot date; authorised take, not actual take. |

The organization-to-region mapping in `scripts/transform.py` is an **operator
grouping proxy**. It does not establish that every customer or network lies inside
the corresponding Stats NZ region. Preserve that qualification in any regional
comparison. Unmapped operators need scope review; they are not automatically
outside the six geographic regions.

## Source fields for water measures

All fields below come from the pinned NEPR 2024/25 extract. Preserve the matching
reason-not-available and provider confidence fields alongside the values in the
normalized `network_records.json`. Annual volumes use m³/year; divide by the documented number
of days in the reporting period to express an annual daily average (365 for
2024/25). An annual average is not peak-day demand.

| Source field | Meaning | Interpretation and missing-value rule |
|---|---|---|
| D-EH3 `Total population served` | Estimated network customers（服务人口） | Not regional resident population. Require a positive value for a per-person denominator. A missing population need not exclude a valid supply volume from its separately labelled reported-volume total. |
| D-EH4 `Total volume of water supplied to network` | Water supplied into a network（管网供水量） | Includes water subsequently used by different customer types or lost. Not household consumption. Keep zero distinct from missing; zero cannot be a loss-rate denominator. |
| D-EH7 `Volume of non-residential water use` | Use by non-residential customers（非居民用水） | Helps explain supply differences; do not infer residential use when this or other balance components are missing. |
| D-RE1 `Total drinking water loss across network` | Reported estimated total water loss（估算总水损） | Not automatically physical leakage or recoverable water. Preserve `Includes private water loss?` as Yes / No / unknown. |
| D-RE2.1 CARL | Estimated current annual real losses（实际物理损失估算） | Leaks, bursts and overflows as defined by the source. Not the amount economically recoverable. |
| D-RE2.2 UARL | Estimated unavoidable annual real losses（理论不可避免损失） | Reference quantity used in ILI. Require a positive denominator for ILI. Not a project-derived repair target. |
| D-RE3 ILI | CARL divided by UARL（漏损指数） | Source-reported network index; check constituent values and pressure context. Do not interpret a population-weighted mean as a region's overall ILI. |
| D-EH1.1 / D-EH2.1 | Residential / non-residential connections（连接数） | Neither is population. If a per-service-connection measure is added, use the documented connection scope; do not silently use residential connections only. |
| D-RE4 | Median residential consumption, L/connection/day（住宅连接用水中位数） | Not per-person consumption; medians cannot be added or averaged to reconstruct a regional median. |
| D-EH5 / D-EH6, organization file | Water imported / exported between suppliers（供水商之间调水） | Needed to assess transfers and possible double counting. Keep at organization grain until an allocation is justified. |

The raw extract's [data dictionary](../data/raw/taumata_nepr/) defines the source
columns. The [Taumata Arowai measures guide](https://www.taumataarowai.govt.nz/assets/Uploads/Network-Performance/Environmental-Performance-Measures-and-Guide-2025.pdf)
distinguishes supply, non-residential use, estimated water loss, CARL, UARL and ILI.
For interpretation, see pp. 23–24 and 32–33. Source attribution and licensing are
in the [manifest](../data/raw/taumata_nepr/MANIFEST.md).

## Water outputs and publication rules

These fields are implemented in `supply_per_capita.json`. Loss totals and paired
contributions are nested under `loss_cohorts`, one each for No / Yes / unknown.
The top-level row `paired_*` fields repeat the default No cohort for the map.

| Measure | Calculation and valid records | Publication rule |
|---|---|---|
| Reported network supply, `reported_supply_m3_year` | Sum valid non-negative D-EH4 values after resolving record identity | State included networks and missing values. This is a sum of network inputs, not a verified unique regional water resource total; transfers need review. |
| Reported estimated water loss, `reported_loss_m3_year` | Sum valid non-negative D-RE1 values for the stated boundary group | Publish No / Yes / unknown private-loss groups separately. A supply-missing record may contribute to a standalone reported-loss subtotal, but not to a supply/loss rate. Flag loss greater than supply for review; exclude it from comparable rates. |
| Comparable aggregate water-loss rate, `paired_loss_pct` | `100 × sum(loss) / sum(supply)` over the **same** networks with positive supply, valid loss no greater than supply, and the same private-loss boundary | Default comparable cohort: private-loss flag No. Show unavailable when no qualifying networks exist. Yes and unknown cohorts remain visible separately; never impute public-only loss. This describes a volume share, not investment priority. |
| Supply per served person, `supply_l_person_day` | `1000 × sum(annual supply) / period_days / sum(served population)` on the same records with valid supply and positive population | Label as network supply per served person, not household consumption or efficiency. State coverage and operator-based geography. |
| Metric network coverage | Qualifying network count / identity-resolved candidate network count | Publish both counts; exclude quarantined identities transparently rather than claiming complete regional coverage. |
| Metric reported-supply coverage | Supply in the metric cohort / supply in all candidate records with valid reported supply | Both sums must use the same reporting period; describes coverage of reported supply only, not all regional supply. |
| Served-population comparison | Not published in v2 | Service geography and overlap are unverified; no claim of connected-resident coverage. |
| Regional supply scenario | Regional ERP × selected supply-per-person rate / 1000 | Optional `scenario_base_supply_m3_day` output. Extends network rates to residents outside reporting networks. Keep separate from reported totals and quantify coverage first. |
| Growth scenario | Selected baseline quantity × `(1 + historical CAGR)^(target_year − base_year)` | A constant-rate scenario, not an official population forecast or a capacity assessment. Network-population growth is not known from regional ERP alone. |
| CARL per connection / aggregate ILI | Further methodological review required | Legacy summaries removed from v2 outputs. Network source values remain available for review. Do not replace them with supply weights without a valid denominator definition. |

Dataset metadata carries source period and calculation version; rows carry
relevant years, counts and coverage. `network_records.json` records exclusions. Round
only the final presentation value; calculate totals and rates from unrounded inputs.

## Version 2 field reference

All quantities are unrounded in JSON. UI values are rounded for reading; a displayed
100% can be a rounded value. `null` is unknown or inapplicable, not zero.

| Fields | Meaning / denominator |
|---|---|
| `candidate_networks` | Identity-resolved records in the operator grouping; excludes conflicts and missing IDs, counts consistent repeated water measures once. |
| `reported_supply_networks`, `reported_supply_m3_year`, `reported_supply_m3_day` | Count and sum of valid non-negative supply; daily value = annual / `period_days`. |
| `supply_population_networks`, `supply_population_supply_m3_year`, `supply_population_served_people` | Count, supply and population in the matched supply/positive-population cohort. Zero supply can contribute to this cohort. |
| `supply_l_person_day` | Matched annual supply × 1000 / period days / matched served population. |
| `supply_population_network_coverage_pct` | Matched supply/population networks / all candidates × 100. |
| `supply_population_supply_coverage_pct` | Matched supply / all valid reported supply × 100. |
| `missing_or_invalid_supply_networks`, `missing_or_invalid_loss_networks`, `loss_above_supply_networks` | Candidate counts for missing or invalid numerics, and loss exceeding known supply; retained as quality information. |
| `loss_cohorts[].boundary` | `No` excludes private loss; `Yes` includes it; `unknown` has no usable answer. Never combine these to publish a comparable rate. |
| `boundary_candidate_networks`, `reported_loss_networks`, `reported_loss_m3_year` (cohort) | Candidates in that boundary, count reporting valid non-negative loss, and their standalone loss sum. This subtotal can include supply-missing or inconsistent records. |
| `paired_networks`, `paired_supply_m3_year`, `paired_loss_m3_year` (cohort) | Only positive supply and non-negative loss no greater than supply, in the same boundary. |
| `paired_loss_pct` (cohort and default row) | 100 × paired loss / paired supply. No eligible records → null; a valid reported zero loss → 0. |
| `paired_network_coverage_pct` (cohort) | Paired count / **all** region-proxy candidates, including the other boundaries, × 100. Counts 0 when a nonempty candidate set has no pairs. |
| `paired_supply_coverage_pct` (cohort and default row) | Paired supply / all valid reported supply × 100. Null when the paired volume is unavailable or the denominator is zero/missing. |
| `loss_above_supply_networks` (cohort) | Inconsistent records in that boundary, excluded from rates but retained in standalone loss totals. |
| `population_base_year`, `population_base` | Latest actual population year and ERP, independently selected per region. |
| `cagr_start_year`, `cagr_end_year`, `cagr5_pct` | Base−5, base, and historical compound annual growth; all six positive yearly observations required. |
| `scenario_horizon_years`, `projection_year`, `scenario_growth_pct` | Five years; actual base+5; 100 × ((1+CAGR)^5−1). Missing CAGR → null growth and future volume. |
| `scenario_base_supply_m3_day`, `scenario_projected_supply_m3_day` | Regional ERP × matched supply/person / 1000; then × historical growth factor. No regional loss estimate is derived. |
| `period_days` | Reporting-period divisor, 365 for the pinned 2024/25 source; independent of population base year. |

Dataset metadata: `schema_version=2`, `calculation_version=network-comparison-v2`,
`source_period`, `period_start`, `period_end`, `source_release`, `source_file`,
`source_sha256`, `geography=operator_region_proxy`, `default_loss_boundary=No`,
`scenario_assumption`, `source_audit`, `processed_utc`, `input_mode`. Source hashes
refer to the actual input file (the excerpt in example mode); `example_provenance`
then links excerpt records to original records and source-file hashes.

`network_records.json` exposes `network_key` (release|account|supply), `account_id`,
`supply_id`, `organization`, `supply_name`, `region`, `private_loss_boundary`,
`source_file`, `source_records` (header = CSV record 1), `raw_values`, `issues`, and
`quality_context` (provider confidence, unavailable reasons and private-loss flag).
Normalized numeric names are `population_served`, `supply_m3_year`, `loss_m3_year`,
`residential_connections`, `nonresidential_connections`, `nonresidential_use_m3_year`,
`carl_m3_year`, `uarl_m3_year`, `ili`, `residential_median_l_connection_day`.
Blank, negative or non-finite numbers become null with an issue; raw strings remain.
Source-reported CARL, UARL, ILI and median consumption are retained, **not aggregated**.

The embedded `audit` lists missing identities, conflicting groups, consistent
repeats and retained source records, mapping inventory and metric missingness.
Organization imports/exports remain in the separate dated audit and raw organization
file; they are not joined or multiplied across networks. Quarantined identity
records are preserved in those source files/audit rather than assigned invented IDs.

Legacy fields (`pop_2025`, `pop_served`, `coverage_pct`, `l_per_person_day_w`,
`loss_pct_w`, `carl_l_conn_day_w`, `ili_w`, `daily_demand_m3`, `leak_m3_day`,
`proj_demand_m3_day`) are removed from v2. Rebuild data and site together. The UI
rejects old water schemas rather than silently using the previous formulas.

## Population and river-flow measures

| Measure / fields | Meaning and calculation | Limitations and missingness |
|---|---|---|
| Population / `pop`, `year` | Estimated residents on 30 June of the given year | Population revision and geography must be recorded. Require unique region/year and positive population. |
| Annual growth / `yoy_growth_pct` | `100 × (P(year) / P(year−1) − 1)` | Missing preceding year means unavailable; do not substitute the preceding available row. |
| Five-year CAGR / `cagr5_pct` | `100 × ((P(year) / P(year−5))^(1/5) − 1)` | Requires all six positive annual observations; not an official future projection. |
| Five-year gain / `pop_gain_5yr` | `P(year) − P(year−5)` | People, not percent; requires all six annual observations in the interval, matching CAGR eligibility. |
| Latest flow / `latest_flow_m3s`, `latest_date`, `units` | Latest valid non-negative daily observation, in m³/s | Latest available can be historical or cached. Keep observation and retrieval dates distinct. |
| Historical percentile / `pctile_pct` | Share of valid daily flows strictly below the latest value × 100, pooled across completed prior seasonal windows | Calendar-date ±7 days in each season year; current season excluded. February 29 anchors to February 28 in non-leap years. Null unless at least 3 seasons each have ≥10 valid days. Project display gate, not a hydrological standard. Ties are not below. |
| Historical sample / `n_history`, `min_hist_m3s`, `median_hist_m3s`, `max_hist_m3s` | Count, minimum, median and maximum of valid observations in the completed prior windows | Statistics remain visible for sparse samples; no history yields null min/median/max. Days are not independent years; years with more observations contribute more to the pooled rank. |
| Flow band / `band` | Below 25 low; 25–75 middle (inclusive); above 75 high; `insufficient` when the multi-year gate fails | Calculated from the unrounded rank. Descriptive bands, not drought thresholds or a climatological normal. |
| Observation age / `stale_days` | Build date minus latest observation date | Age at calculation time; it does not update just because a browser opens later. Source-specific freshness rules remain pending. |
| Consented share / `activities.*.share_pct` | Source snapshot's share of authorised volume assigned to an activity | No actual consumption or water remaining can be inferred. Missing region data is unavailable, not zero. |

## Seasonal flow v2: coverage and year semantics

A **season year** names the centre of a 15-day window, not the calendar years of
its individual observations. For a January 3 comparison, the 2025 season is
December 27, 2024 through January 10, 2025. It counts as one season. For a latest
observation on January 3, 2026, the unfinished December 27, 2025–January 10, 2026
window is excluded entirely. No current-season observations enter the baseline.

For each year, construct the actual month/day and add/subtract seven calendar
days. February 29 uses February 28 **only in non-leap years**, an explicit project
convention. March dates keep their month/day. SQL uses calendar arithmetic rather
than shifting day-of-year numbers; see [DuckDB date functions](https://duckdb.org/docs/current/sql/functions/date).

| Fields | Definition and null rule |
|---|---|
| `n_history`, `n_below_latest` | Valid observed daily values in all completed prior windows; number strictly below the unrounded latest value. Zero flow is valid; negative/non-finite values are excluded. |
| `n_history_seasons` | Number of completed seasonal windows overlapping the valid source observation span. A window must end before latest observation and on/after first observation. Empty intervening seasons count. |
| `n_history_years` | Seasons with at least one observed day, not calendar-year count and not elapsed-year span. |
| `n_qualified_years` | Seasons with at least 10 of 15 daily observations. At least 3 are required to show a percentile; sparse prior seasons still contribute their observed days to the pooled rank when the gate passes. |
| `history_year_start`, `history_year_end` | Earliest/latest included season centre year, including empty seasons within the source span. Null if no prior window exists. |
| `history_first_date`, `history_last_date` | Actual earliest/latest daily observations used in historical statistics. Null if no historical observation exists. |
| `expected_history_days` | 15 × `n_history_seasons`. Includes potential days before the first observation in a partially observed first season; not verified station operating days. |
| `history_coverage_pct` | 100 × `n_history` / `expected_history_days`; null if there are no windows. Missing years stay in this denominator. It measures seasonal sample coverage, not station uptime or current-data freshness. |
| `history_years[]` | Per-season `season_year`, `observed_days`, `expected_days` (15), `qualifies` (≥10 observations). Empty intervening seasons report zero observed days. |
| `history_status` | `sufficient` when the project gate passes; otherwise `insufficient_years`, with null `pctile_pct` and band `insufficient`. A valid zero percentile is different from a missing rank. |
| `policy` (dataset) | `seasonal-history-v2`, window radius, minimum years/days, leap-day convention, current-season exclusion and pooling rule; configured in `scripts/flow_policy.py`. |
| `council_snapshot_fetched_utc` (dataset) | Retrieval timestamp of each source council snapshot, distinct from each site's observation date and output processing time; a snapshot can contain cached site records. |

The 3-season / 10-day gate is a pragmatic project screening rule: it prevents a
handful of days or one/two seasons being presented as a supported historical rank.
It does not establish representativeness, independence, a long-term climate normal,
or a drought diagnosis. Seasonal coverage, sample years and observation date remain
necessary even for a displayed rank. The source span is not a certified station
operation record. No values are filled across gaps.

## Validation and remaining limitations

Production and offline examples use the same normalizer, SQL and schema validation.
The validator independently reconciles reported sums, matched contributions, rates,
coverage and scenario years to network records and population. An independent
Python date calculation also reconciles each flow window, per-year count, sample
coverage, statistics, rank and band to daily source observations. Core tests build
examples when no explicit output folder is supplied; missing files are errors.
The [fixture manifest](../fixtures/offline/MANIFEST.json) preserves source attribution.

Flow snapshots preserve raw observations. Invalid/negative observations are excluded
from analysis and listed under `quality.excluded_observations`; zero remains valid.
Duplicate daily keys fail the build rather than silently averaging them. The v2 calendar-window fix and multi-year history display gate are now applied.
Freshness is calculated from an explicit build date, fixed in offline examples.

Passing validation does not verify provider estimates, resolve service geography,
reconcile transfers, establish recoverable water, or validate investment decisions.
