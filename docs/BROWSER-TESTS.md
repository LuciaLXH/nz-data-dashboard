# Source endpoint checks

These notes record manual endpoint checks performed on 2026-08-30. They are
historical observations, not a guarantee of current service availability.
The automated pipeline records current fetch status separately.

## Interpreting responses

- Hilltop requests require `Service=Hilltop` and a `Request` parameter. Valid
  responses are XML; an HTML information page without parameters is expected.
- ArcGIS service pages expose metadata; `/query` returns records. Use `f=pjson`
  for readable JSON and `resultRecordCount=5` for a small sample query.
- A web-server welcome page at the root domain does not establish whether a
  specific data endpoint is working.

## Hilltop

| Provider | Check | Request URL |
|---|---|---|
| ORC | Site list | `http://gisdata.orc.govt.nz/hilltop/Global.hts?Service=Hilltop&Request=SiteList` |
| ORC | Measurements | `http://gisdata.orc.govt.nz/hilltop/Global.hts?Service=Hilltop&Request=MeasurementList&Site=Arrow%20at%20Cornwall%20street%20d%2Fs` |
| ORC | Historical flow | `http://gisdata.orc.govt.nz/hilltop/Global.hts?Service=Hilltop&Request=GetData&Site=Arrow%20at%20Cornwall%20street%20d%2Fs&Measurement=Flow%20%5BWater%20Level%5D&From=2020-01-01&To=2020-01-31` |
| HBRC | Site list | `https://data.hbrc.govt.nz/Envirodata/EMAR.hts?Service=Hilltop&Request=SiteList` |
| HBRC | Measurements | `https://data.hbrc.govt.nz/Envirodata/EMAR.hts?Service=Hilltop&Request=MeasurementList&Site=Ngaruroro%20River%20at%20Fernhill` |
| HBRC | Flow sample | `https://data.hbrc.govt.nz/Envirodata/EMAR.hts?Service=Hilltop&Request=GetData&Site=Ngaruroro%20River%20at%20Fernhill&Measurement=FlowM3S%20%5BWater%20Level%5D&From=2026-08-27&To=2026-08-30` |

ORC's checked public endpoint exposed historical observations from 2010-12-29
to 2021-04-23. Requests for a 2026 window returned no data. The fetcher uses
the availability window in `MeasurementList` and the `Flow [Water Level]`
measurement; cumecs and m³/s are equivalent.

HBRC's `SiteList` primarily returned historical sites. Direct requests worked
for the curated telemetry sites: Ngaruroro River at Fernhill, Tukituki River
at Red Bridge, and Mohaka River at Raupunga. Their measurement was
`FlowM3S [Water Level]`, with 15-minute observations in the checked sample.

Both checked servers ignored `Interval=P1D`; daily means are calculated in
Python. Encode spaces as `%20`: HBRC rejected `+` encoding in the checks.

## ArcGIS

| Provider | Service metadata | Sample query and scope |
|---|---|---|
| ECan | `https://gis1.ecan.govt.nz/arcgis/rest/services/Public/Well_Drillers/MapServer/13?f=pjson` | Append `/query?where=1%3D1&returnGeometry=false&outFields=*&f=json&resultRecordCount=5` before the metadata query string. Layer 13 exposed River Flow and Stage site metadata, not flow time series. |
| Southland | `https://maps.es.govt.nz/server/rest/services/Public/RiversRainfall/MapServer?f=pjson` | Layer 0 `/query` exposed soil-moisture records, not river flow. |
| Auckland | `https://mapspublic.aucklandcouncil.govt.nz/arcgis3/rest/services/NonCouncil/LAWA/MapServer?f=pjson` | Layer 0 `/query` exposed monitoring-site reference data, not flow time series. |

The ECan service name `Well_Drillers` does not describe layer 13's contents.
Always inspect layer fields before treating a response as hydrological data.

## Checks requiring follow-up

- The candidate Waikato host `data.waikatoregion.govt.nz` could not be reached
  during the checks; this does not prove that Waikato has no accessible data.
- The legacy Stats NZ host `api.stats.govt.nz` returned HTTP 502 during the
  checks. The pipeline subsequently adopted the SDMX endpoint documented in
  the [source registry](W1-data-sources.md).
