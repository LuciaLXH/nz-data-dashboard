# Data source registry

Initial checks: 2026-08-30. Maintenance notes updated: 2026-10-22.
Endpoint behaviour below describes those checks; access and coverage may change.

## River flow

| Provider | Endpoint | Observed scope |
|---|---|---|
| Hawke's Bay Regional Council | `https://data.hbrc.govt.nz/Envirodata/EMAR.hts` | Live Hilltop telemetry for three curated sites. Direct requests are needed because `SiteList` primarily exposed historical sites. |
| Otago Regional Council | `http://gisdata.orc.govt.nz/hilltop/Global.hts` | Historical Hilltop flow for eight curated sites, ending in April 2021 at this endpoint. |
| Environment Canterbury | `https://gis1.ecan.govt.nz/arcgis/rest/services/Public/Well_Drillers/MapServer/13` | River Flow and Stage site metadata; no time series found in this layer. |
| Environment Southland | `https://maps.es.govt.nz/server/rest/services/Public/` | Soil-moisture series, catchment polygons, and site metadata were found; a usable flow series was not identified. |
| Auckland Council | `https://mapspublic.aucklandcouncil.govt.nz/arcgis3/rest/services/NonCouncil/LAWA/MapServer` | Monitoring-site reference data. |
| Waikato Regional Council | Candidate Hilltop hosts | Connection or HTML error responses during the checks; integration remains pending. |

`scripts/fetch_hilltop.py` retrieves HBRC and ORC observations and calculates
daily means. ORC uses `Flow [Water Level]` in cumecs; HBRC uses
`FlowM3S [Water Level]` in m³/s. The fetcher reads measurement availability
windows, encodes spaces as `%20`, and retains cached site series when a request
fails or returns no observations. Fresh fetches and fallback coverage are
reported separately. See [endpoint checks](BROWSER-TESTS.md) for sample requests.

These findings concern the inspected endpoints. They do not establish that
other providers have no public flow data through different services.

## Population

The pipeline uses Stats NZ's SDMX dataflow:

`https://api.data.stats.govt.nz/rest/data/STATSNZ,POPES_SUB_001,1.0/ALL`

Authentication uses `Ocp-Apim-Subscription-Key`, supplied through an environment
variable. The checked request used the Accept header
`application/vnd.sdmx.data+json; charset=utf-8; version=1.0.0-wd`.
The full key `ALL` is filtered locally; abbreviated keys returned no records
in the initial checks. The legacy OData endpoint returned HTTP 502 at that time.

The initial snapshot covered six regions for 2018–2025, including estimated
resident population, median age, and net migration. Regional codes were checked
against the SDMX codelist: Auckland 02, Waikato 03, Hawke's Bay 06, Canterbury 13,
Otago 14, and Southland 15. `data/ref/region_map.json` stores these mappings.

## Water supply, leakage, and metering

The primary analytical input is Taumata Arowai's NEPR 2024/25 unit-level CSV
extract, retained under `data/raw/taumata_nepr/` with its source manifest and
CC BY 3.0 NZ attribution. `data/ref/water_demand.json` also records selected
supplier metrics and historical NPR comparisons.

Water New Zealand's final NPR edition was 2021/22. A local research extract
from its public Tableau dashboard covered 574 supplier-year rows across nine
years. Large reports and exploratory extracts are not distributed with this repo.
See [NPR and NEPR research](NPR-research.md) and the
[Dunedin/Invercargill notes](W1-water-demand-dunedin-invercargill.md) for metric
definitions, reporting differences, quality flags, and source references.

Supply per person is derived from reported supply divided by served population;
it is not necessarily residential consumption. The local v2 dashboard prioritizes reported network supply and matched loss
cohorts with coverage. Regional population scenarios are separate; no regional
loss volume is inferred. Network-input sums may include transfers. See the
[data dictionary](DATA-DICTIONARY.md); the [2026-10-10 review](REVIEW-2026-10-10.md)
records the earlier scenario-based implementation.

## Geographic mapping

The LAWA boundary service `/umbraco/api/mapservice/boundaryforNZ` supplied WKT
geometry used for `data/ref/boundaries_regions_simple.geojson` (approximately
4.9 KB after simplification). Attribution follows LAWA's CC BY 4.0 terms;
the underlying regional council boundaries are derived from Stats NZ.

Region aliases were checked against 11,004 LAWA river-quality records. All
5,954 records within the six selected regions matched the expected mapping;
the remaining regions were outside scope.

The supplier-to-region mapping in `scripts/transform.py` groups territorial
authorities by region. Population cross-checks matched regional totals exactly
for Auckland, Hawke's Bay, and Southland over the eight checked years. Differences
of approximately 0.3–0.7% in the other regions were consistent with territorial
authorities crossing regional boundaries. These aggregate checks do not verify individual service geography. The mapping
remains an operator grouping proxy; see the [source audit](SOURCE-AUDIT-2026-10-22.md).

## Water quality and land cover

Seven LAWA workbooks were downloaded locally on 2026-08-30 from
[LAWA's download page](https://www.lawa.org.nz/download-data). They cover river
quality, river ecology, lakes, groundwater, recreational quality, and land cover.
The local source manifest records URLs and SHA-256 hashes; these large raw
workbooks are excluded from Git. Their analysis is not part of the current
supply-pressure findings.

The river-quality workbook includes state quartiles, attribute bands, and trends;
region names require normalization. Land-cover tables contain regional and
catchment areas for 1996–2018. Water-quality and land-use analysis remains pending.

## Candidate integrations

LAWA's explorer exposed internal Umbraco routes for flow sites, flow statistics,
available water, and usage. These are research leads rather than a stable public
API contract. Regional rainfall/runoff summaries must not be treated as urban
network supply. New integrations require endpoint, metric, licence, and
coverage checks before inclusion.

## Maintenance

Flow and population are requested on each scheduled run. NEPR, LAWA, and other
reference snapshots require manual updates, dated attribution, and validation.
An annual source publication does not become current merely because the site
has a recent build timestamp.
