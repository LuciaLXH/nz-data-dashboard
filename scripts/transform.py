"""W1-minimal transform: package raw snapshots → data/processed/*.json.

Full W2 version replaces this with DuckDB + sql/01-03 (all business logic in
SQL; Python does IO/orchestration only). This version just moves/annotates raw
JSON so `make data` runs end-to-end from scratch:
  - data/processed/flow.json     — flow snapshot + status (from data/raw/flow/)
  - data/processed/regions.json  — region map + boundary status (from data/ref/)
  - data/processed/population.json — population fetch status (from data/raw/population/)
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import datetime, timezone


def _load(path: str, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def _flow_snapshot() -> dict:
    """Latest flow snapshot per council + overall status."""
    status = _load("data/raw/flow/_status.json", {})
    snapshots: dict[str, dict] = {}
    for council in ("hbrc", "orc"):
        files = sorted(glob.glob(f"data/raw/flow/{council}/*.json"))
        if files:
            snapshots[council] = _load(files[-1], {})
    return {
        "schema_version": 1,
        "source": "council Hilltop servers (see docs/W1-data-sources.md)",
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
        "councils": snapshots,
        "status": status,
    }


def main() -> int:
    os.makedirs("data/processed", exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    flow = _flow_snapshot()
    with open("data/processed/flow.json", "w", encoding="utf-8") as f:
        json.dump(flow, f, ensure_ascii=False, indent=1)

    regions = {
        "schema_version": 1,
        "source": "data/ref/region_map.json (REGC ↔ council ↔ LAWA zone)",
        "regions": _load("data/ref/region_map.json", {}).get("regions", []),
    }
    with open("data/processed/regions.json", "w", encoding="utf-8") as f:
        json.dump(regions, f, ensure_ascii=False, indent=1)

    population = {
        "schema_version": 1,
        "status": _load("data/raw/population/_status.json",
                        {"ok": False, "note": "no population fetch attempted"}),
        "processed_utc": now,
    }
    pop_files = sorted(glob.glob("data/raw/population/[0-9]*.json"))
    if pop_files:
        population["data"] = _load(pop_files[-1], {})
    with open("data/processed/population.json", "w", encoding="utf-8") as f:
        json.dump(population, f, ensure_ascii=False, indent=1)

    n_flow = sum(len(v.get("sites", [])) for v in flow["councils"].values())
    n_pop = len(population.get("data", {}).get("regions", {}))
    print(f"transform: flow sites={n_flow} | regions={len(regions['regions'])} | "
          f"population regions={n_pop} ok={population['status'].get('ok')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
