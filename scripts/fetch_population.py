"""Fetch subnational population estimates (6 regional councils) from Stats NZ.

W1 (2026-08-30): the old ADE OData API (api.stats.govt.nz/opendata) has been
down (502) all session. The successor API works — SDMX at
https://api.data.stats.govt.nz/rest (dotstatsuite; the backend behind the new
explore.data.stats.govt.nz) with the same Ocp-Apim-Subscription-Key.

Dataflow: STATSNZ:POPES_SUB_001(1.0) — subnational population estimates
(2018-base, ERP), dimensions YEAR_POPES_SUB_001 × AREA_POPES_SUB_001 ×
MEASURE_POPES_SUB_001 (POP, MEDAGE, NETMIG, ...). Areas use Stats NZ numeric
codes: Auckland=02, Waikato=03, Hawke's Bay=06, Canterbury=13, Otago=14,
Southland=15 (verified from the API codelist — these differ from the older
REGC scheme where Canterbury was 14).

Notes from debugging (2026-08-30):
- year wildcards ('A'/'ALL' in the YEAR position) return NoRecordsFound;
  the full-key query `.../ALL` works and returns every observation.
- dimensionAtObservation must name a real dimension; TIME_PERIOD is invalid.

Output: data/raw/population/<YYYYMMDD>.json — {council: {year: pop}} plus
MEDAGE and NETMIG, and _status.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

SDMX_BASE = "https://api.data.stats.govt.nz/rest/data/STATSNZ,POPES_SUB_001,1.0"
ACCEPT = "application/vnd.sdmx.data+json; charset=utf-8; version=1.0.0-wd"
TIMEOUT = 90

# area code -> region key (verified from the API codelist, 2026-08-30)
AREA_TARGETS = {
    "02": "auckland",
    "03": "waikato",
    "06": "hawkes_bay",
    "13": "canterbury",
    "14": "otago",
    "15": "southland",
}
MEASURE_TARGETS = {"POP", "MEDAGE", "NETMIG"}


def fetch(retries: int = 3) -> tuple[dict, str]:
    """Fetch ALL observations; returns (data, raw_text). Retries with
    exponential backoff (W3: resilient scheduled runs); raises on final
    failure so main() records a degraded _status.json."""
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(f"{SDMX_BASE}/ALL",
                             headers={"Ocp-Apim-Subscription-Key": os.environ["STATS_NZ_API_KEY"],
                                      "Accept": ACCEPT},
                             timeout=TIMEOUT)
            r.raise_for_status()
            return r.json(), r.text
        except Exception as e:  # noqa: BLE001 — network errors vary
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * (2 ** (attempt - 1)))
    assert last_err is not None
    raise last_err


def main() -> int:
    key = os.environ.get("STATS_NZ_API_KEY")
    if not key:
        raise SystemExit("STATS_NZ_API_KEY is not set — see .env.example")
    try:
        doc, raw = fetch()
    except Exception as e:  # noqa: BLE001 — graceful degradation
        now = datetime.now(timezone.utc).isoformat()
        os.makedirs("data/raw/population", exist_ok=True)
        with open("data/raw/population/_status.json", "w", encoding="utf-8") as f:
            json.dump({"ok": False, "note": f"fetch failed: {e}", "attempted_utc": now}, f, indent=1)
        print(f"⚠️ Stats NZ SDMX: fetch failed ({e}) — recorded for Data Health")
        return 0

    sv = doc["data"]["structure"]["dimensions"]["observation"]
    year_vals, area_vals, measure_vals = ([v["id"] for v in x["values"]] for x in sv)
    obs = doc["data"]["dataSets"][0]["observations"]

    # {region: {year: {measure: value}}}
    result: dict[str, dict[str, dict[str, float]]] = {}
    for okey, oval in obs.items():
        yi, ai, mi = (int(x) for x in okey.split(":"))
        area, measure = area_vals[ai], measure_vals[mi]
        region = AREA_TARGETS.get(area)
        if not region or measure not in MEASURE_TARGETS:
            continue
        year = year_vals[yi]
        value = oval[0] if isinstance(oval, list) else oval
        result.setdefault(region, {}).setdefault(year, {})[measure] = value

    now = datetime.now(timezone.utc).isoformat()
    os.makedirs("data/raw/population", exist_ok=True)
    stamp = now[:10].replace("-", "")
    path = f"data/raw/population/{stamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "source": f"{SDMX_BASE}/ALL",
            "dataflow": "STATSNZ:POPES_SUB_001(1.0)",
            "fetched_utc": now,
            "measures": sorted(MEASURE_TARGETS),
            "areas": AREA_TARGETS,
            "regions": {r: {y: v for y, v in sorted(years.items())}
                        for r, years in sorted(result.items())},
        }, f, ensure_ascii=False, indent=1)
    with open("data/raw/population/_status.json", "w", encoding="utf-8") as f:
        json.dump({"ok": True, "file": path, "fetched_utc": now}, f, indent=1)

    n = sum(len(years) for years in result.values())
    print(f"✅ Stats NZ SDMX: {len(result)} regions × {n} region-years → {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
