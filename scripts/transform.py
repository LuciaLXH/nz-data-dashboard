"""Transform raw snapshots → data/processed/*.json via DuckDB (sql/).

All business logic lives in sql/; this module only orchestrates IO:
  1. package raw flow / regions / population snapshots (W1 shape, unchanged)
  2. load population into DuckDB, run each sql/ analysis, export the result
     as data/processed/<name>.json (W2+).

Runs are recorded by scripts/validate.py into data/processed/_runs.jsonl.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import datetime, timezone

import duckdb

SQL_OUTPUTS = [
    # (sql file, output json name, expected top-level key of the result rows)
    ("sql/01_region_population_growth.sql", "population_growth.json", "rows"),
]

REGION_ORDER = ["auckland", "waikato", "hawkes_bay", "canterbury", "otago", "southland"]


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


def _population_records(raw_pop: dict) -> list[dict]:
    """Flatten data/raw/population/<stamp>.json → DuckDB rows."""
    rows = []
    for region, years in raw_pop.get("regions", {}).items():
        for year, measures in years.items():
            rows.append({
                "region": region,
                "year": int(year),
                "pop": measures.get("POP"),
                "medage": measures.get("MEDAGE"),
                "netmig": measures.get("NETMIG"),
            })
    return rows


def _run_sql_analyses(population_raw: dict) -> list[dict]:
    """Run each sql/ analysis against DuckDB; returns [{name, key, sql_file, rows}]."""
    import pandas as pd

    con = duckdb.connect()
    rows = _population_records(population_raw)
    if rows:
        con.register("population", pd.DataFrame(rows))
    results = []
    for sql_file, out_name, key in SQL_OUTPUTS:
        sql = open(sql_file, encoding="utf-8").read()
        rel = con.execute(sql)
        result_rows = [dict(zip([d[0] for d in rel.description], r)) for r in rel.fetchall()]
        results.append({"name": out_name, "key": key, "sql_file": sql_file, "rows": result_rows})
    con.close()
    return results


def main() -> int:
    os.makedirs("data/processed", exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    # 1) W1 packaging (unchanged shape)
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

    pop_files = sorted(glob.glob("data/raw/population/[0-9]*.json"))
    population_raw = _load(pop_files[-1], {}) if pop_files else {}
    population = {
        "schema_version": 1,
        "status": _load("data/raw/population/_status.json",
                        {"ok": False, "note": "no population fetch attempted"}),
        "processed_utc": now,
    }
    if population_raw:
        population["data"] = population_raw
    with open("data/processed/population.json", "w", encoding="utf-8") as f:
        json.dump(population, f, ensure_ascii=False, indent=1)

    # 2) W2 analyses via DuckDB + sql/
    analyses = _run_sql_analyses(population_raw)
    for item in analyses:
        out = {
            "schema_version": 1,
            "sql": item["sql_file"],
            "processed_utc": now,
            item["key"]: item["rows"],
        }
        with open(f"data/processed/{item['name']}", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)

    n_flow = sum(len(v.get("sites", [])) for v in flow["councils"].values())
    n_pop = len(population_raw.get("regions", {}))
    n_growth = len(analyses[0]["rows"]) if analyses else 0
    print(f"transform: flow sites={n_flow} | regions={len(regions['regions'])} | "
          f"population regions={n_pop} | growth rows={n_growth}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
