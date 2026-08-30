"""Fetch subnational population estimates (6 regional councils) from Stats NZ
Aotearoa Data Explorer (ADE) OData API.

Endpoint: https://api.stats.govt.nz/opendata/v1/odata/<dataset>
Header   : Ocp-Apim-Subscription-Key: <key from env STATS_NZ_API_KEY>

W1 status (2026-08-30): the ADE backend is returning HTTP 502 (Azure
Application Gateway) — DNS/TLS fine, key activated and valid. This script
therefore implements retry + exponential backoff + graceful degradation:
on failure it records an honest status file and exits 0, so `make data`
still runs from scratch. The exact population dataset OData query is wired
up for the moment the API recovers (see fetch_dataset()).

Output: data/raw/population/ (raw snapshots when the API is up)
        data/raw/population/_status.json (last attempt status, always written)
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

ADE_BASE = "https://api.stats.govt.nz/opendata/v1/odata"
# Dataset + OData query for subnational population estimates by regional
# council (REGC), yearly. TODO(W1.5): confirm exact dataset name + dimension
# codes against the live API when the 502 clears, then enable.
POPULATION_DATASET = "SubnationalPopulationEstimates"
POPULATION_QUERY = (
    f"{POPULATION_DATASET}"
    "?$select=Year,REGC2023,REGC2023_name,Value"
    "&$filter=REGC2023 in ('02','03','06','14','15','16')"
)
MAX_ATTEMPTS = 3
BACKOFF = [5, 15, 45]  # seconds between attempts


def attempt(api_key: str) -> tuple[bool, dict]:
    """One retry loop; returns (ok, status_detail). Never raises."""
    detail: dict = {"attempts": 0, "last_status": None, "last_error": None}
    for attempt_no in range(1, MAX_ATTEMPTS + 1):
        detail["attempts"] = attempt_no
        try:
            r = requests.get(
                f"{ADE_BASE}/{POPULATION_QUERY}",
                headers={"Ocp-Apim-Subscription-Key": api_key},
                timeout=30,
            )
            detail["last_status"] = r.status_code
            if r.status_code == 200:
                data = r.json()
                rows = data.get("value", [])
                if not rows:
                    detail["last_error"] = "200 OK but empty value array (check query)"
                    return False, detail
                return True, detail
            if r.status_code in (403, 429, 500, 502, 503, 504):
                # 403 observed once while the gateway is flaky (root returns
                # 502) — treat as retryable, but record the status each time.
                if attempt_no < MAX_ATTEMPTS:
                    time.sleep(BACKOFF[attempt_no - 1])
                continue
            detail["last_error"] = f"non-retryable HTTP {r.status_code}: {r.text[:200]}"
            return False, detail
        except requests.RequestException as e:
            detail["last_error"] = str(e)
            if attempt_no < MAX_ATTEMPTS:
                time.sleep(BACKOFF[attempt_no - 1])
    return False, detail


def main() -> int:
    key = os.environ.get("STATS_NZ_API_KEY")
    if not key:
        # config error → hard fail (not a transient API problem)
        raise SystemExit("STATS_NZ_API_KEY is not set — see .env.example")

    os.makedirs("data/raw/population", exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    ok, detail = attempt(key)

    if ok:
        # TODO(W1.5): write the snapshot rows to data/raw/population/…json
        # once the live query shape is confirmed (see POPULATION_QUERY).
        status = {"ok": True, "note": "API reachable; snapshot writing lands in W1.5",
                  "attempted_utc": now, **detail}
    else:
        status = {
            "ok": False,
            "note": "Stats NZ ADE unavailable (HTTP 502 backend since 2026-08-30); "
                    "recorded for Data Health — pipeline continues degraded",
            "attempted_utc": now, **detail,
        }
    with open("data/raw/population/_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=1)
    print(f"{'✅' if ok else '⚠️'} Stats NZ ADE: status={detail['last_status']} "
          f"attempts={detail['attempts']}")
    return 0  # graceful: record and continue (decision: degrade, don't hard-fail)


if __name__ == "__main__":
    sys.exit(main())
