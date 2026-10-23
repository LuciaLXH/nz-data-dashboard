# Analysis and interpretation

Updated: 2026-10-23. The local v2 pipeline implements the audited identity,
matching, reporting-boundary and year rules. Earlier savings and investment
claims remain withdrawn. Reported network measures, coverage and optional
population scenarios are now separated. This revision is not yet deployed.
See the [data dictionary](docs/DATA-DICTIONARY.md) and
[source audit](docs/SOURCE-AUDIT-2026-10-22.md).

## Project question

How do population growth, network supply and water loss compare across six NZ
regions? The intended use is to identify differences and questions for further
investigation. The available data does not support ranking supply-zone shortages,
forecasting drought, or choosing the cheapest infrastructure intervention.

## What can be investigated

### Network supply per served person

NEPR D-EH4 describes water supplied to a network. Dividing by served population
does not turn that volume into household consumption. Customer mix, non-residential
use, water losses, metering and reporting practices can affect the result.

Auckland can be a comparison point, but this project has not established its
supply-per-person value as an achievable target for other networks. The previous
Hawke's Bay savings comparison used different population scopes on its two sides;
matching those scopes alone would still not establish recoverable savings.

The v2 comparison uses resolved identities and matched supply/population records,
with reporting coverage and the operator-based geographic qualification. Do not infer a causal effect of metering from six
regional comparisons.

### Estimated water loss and reporting coverage

The raw data distinguishes estimated total water loss, current annual real losses
(CARL) and whether private-side losses are included. A report of loss is not a
measurement of the water that repair work could economically recover.

The v2 rate uses summed loss divided by summed supply on the same valid networks
and reporting boundary. It replaces the former population-weighted average. Missingness is material: after the audit's
identity decisions, 44 of 268 candidate records lack a loss value. Southland's
candidates all include private-side losses, so a public-side-only rate cannot be
calculated for that group from the present extract.

The identity audit also found OTO001 assigned to two differing source records.
The old loader mixed their column maxima; v2 quarantines both records. It also
quarantines Albury's missing identifier and counts Riverton's repeated water measures
once while retaining both source references. Organization
imports/exports need consideration before network-input sums are described as
unique regional water volumes.

An annual daily-average volume is not a peak-demand constraint. Neither total
reported loss nor a whole-region loss scenario establishes years of capacity
headroom, project costs or the sequence of repair versus capacity investments.

### Dated flow observations

The pipeline integrates three HBRC telemetry sites and eight ORC sites with
historical records. Each percentile compares one site's latest available daily
observation with a selected seasonal historical sample. Observation date, sample
coverage and measurement unit matter more than the page's build date.

This is coverage of the project's selected sites, not proof that other councils
publish no flow data. The sites are not linked to individual drinking-water
networks, and flow percentiles cannot be substituted for supply capacity.
The v2 window uses actual calendar dates, crosses New Year and treats February 29
as February 28 in non-leap years. The unfinished current season is excluded.
A rank requires at least three prior seasons with at least ten daily observations
each. Counts and seasonal day coverage remain visible, including missing years.
This project display gate is not a hydrological standard; bands are descriptive,
not drought classifications or long-term climate normals.

## Scenarios and time

The existing regional scenario multiplies regional resident population by network
supply per served person, extending the rate to people outside the reporting
networks. It then extends historical five-year population CAGR for another five
years. This is an assumption-based extrapolation, not an official demographic
projection or a demand–supply model.

The current local population snapshot ends in 2025, so the scenario targets 2030.
These are output fields, not fixed labels: a future 2026 base will target 2031.
Year-on-year growth joins year−1; five-year growth requires all six positive annual
observations from base−5 through base. Gaps produce an unavailable growth estimate,
not an extension from a different year. The water rate remains the explicitly
labelled 2024/25 rate even when population changes.

## Reconciled snapshot, not a ranking

The following table comes from the pinned full NEPR extract and v2 SQL, rebuilt
locally on 2026-10-22 without fetching new source data. It is **not** the small
offline example. Loss rates exclude private-side losses and use matched positive
supply/non-negative loss pairs with loss no greater than supply.

| Operator grouping | Candidate networks | Networks in default loss rate | Paired loss rate | Share of reported supply in those pairs |
|---|---:|---:|---:|---:|
| Auckland | 25 | 10 | 19.6% | 100.0%¹ |
| Canterbury | 97 | 63 | 29.7% | 94.7% |
| Hawke's Bay | 19 | 10 | 26.3% | 54.0% |
| Otago | 45 | 19 | 21.6% | 25.1% |
| Southland | 15 | 0 | Unavailable | Unavailable |
| Waikato | 67 | 35 | 19.9% | 33.0% |

¹ Rounded to one decimal; the exact Auckland fraction is below 100%. JSON retains
unrounded contributions. Coverage is of valid **reported network inputs**, not
all regional supply. Candidate counts already exclude quarantined identities.

The important finding here is unequal comparability. For example, the default
Otago rate describes only about a quarter of valid reported network supply.
Southland has no default-boundary result; its separate private-loss-included
cohort remains available. Neither case supports a region-wide efficiency ranking.

## Scope and context

Population describes six geographic regions. Network data is grouped through 34
selected operators, whose service boundaries are not verified against those
regions. The phrase “all registered supplies” is therefore inappropriate.
Reported network population divided by regional ERP is an approximate comparison,
not a verified connected-population coverage rate.

The LAWA consent chart shows the snapshot's allocation of authorised take by use
category. It does not measure actual consumption or water remaining, and it does
not complete a supply-capacity model. Water-quality and land-use analysis is
deferred; no finding about their relative explanatory power has been established.

## Conditions for revised findings

Publish each finding with its source period, unit, valid-record set, coverage,
assumptions and known exclusions. Reconcile headline values to per-network
contributions. Validate the actual pipeline using attributed offline inputs and
targeted boundary cases, then update the README, charts and narrative together.

The [roadmap](docs/PLAN.md) distinguishes local implementation from deployment
and the outstanding source-freshness and geographic work. The [Chinese change record](docs/CHANGELOG.zh-CN.md)
explains the adjustments without requiring knowledge of SQL or data engineering.
