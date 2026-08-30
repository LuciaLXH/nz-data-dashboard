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
    ("sql/02_supply_per_capita.sql", "supply_per_capita.json", "rows"),
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


# Org (NEPR participant) → project region. Orgs outside the 6 regions map to
# None and are excluded from the analysis (they are out of scope, not missing).
#
# Verification (2026-08-30): each territorial authority belongs to exactly one
# regional council (Stats NZ geographic areas). This mapping was checked
# numerically against the official Stats NZ SDMX population data: summing the
# TA-level 2025 ERPs per region matches the regional-council ERP exactly for
# Auckland / Hawke's Bay / Southland (all 8 years), and within 0.3–0.7% for
# Waikato / Canterbury / Otago — the residual is the documented Stats NZ
# split-TA effect (≈3,850 of Taupō District classified to Bay of Plenty;
# ≈1,900 of Waitaki District classified to Canterbury), not a mapping error.
# Council-level assignment is the correct level for water infrastructure.
ORG_REGION = {
    "Watercare": "auckland", "Auckland Council": "auckland", "Papakura": "auckland",
    "Hamilton City Council": "waikato", "Waikato District Council": "waikato",
    "Taupo District Council": "waikato", "South Waikato District Council": "waikato",
    "Waitomo District Council": "waikato", "Otorohanga District Council": "waikato",
    "Thames Coromandel District Council": "waikato", "Waipa District Council": "waikato",
    "Matamata Piako District Council": "waikato", "Hauraki District Council": "waikato",
    "Christchurch City Council": "canterbury", "Selwyn District Council": "canterbury",
    "Waimakariri District Council": "canterbury", "Ashburton District Council": "canterbury",
    "Hurunui District Council": "canterbury", "Kaikoura District Council": "canterbury",
    "Mackenzie District Council": "canterbury", "Timaru District Council": "canterbury",
    "Waimate District Council": "canterbury",
    "Dunedin City Council": "otago", "Central Otago District Council": "otago",
    "Queenstown Lakes District Council": "otago", "Clutha District Council": "otago",
    "Waitaki District Council": "otago",
    "Invercargill City Council": "southland", "Southland District Council": "southland",
    "Gore District Council": "southland",
    "Napier City Council": "hawkes_bay", "Hastings District Council": "hawkes_bay",
    "Central Hawke's Bay District Council": "hawkes_bay", "Wairoa District Council": "hawkes_bay",
}

NEPR_NETWORK_CSV = ("data/raw/taumata_nepr/"
                    "NEPM Final Data Extract for Release 27072026 DW_Network.csv")


def _nepr_network_rows() -> list[dict]:
    """Dedupe the NEPR unit-level CSV → one row per supply with region mapping.

    Columns of interest (NEPM 2024/25 data dictionary):
      D-EH3  Total population served
      D-EH4  Total volume of water supplied to network (m³/yr)
      D-RE1  Total drinking water loss across network (m³/yr)
      D-RE2.1 CARL (m³/connection/day)
      D-RE3  Infrastructure leakage index (ILI)
      D-RE4  Median residential water consumption (L/connection/day)
    Metering % is NOT published in the unit-level extract (only a per-supply
    counting method); metering figures for the 9 main urban suppliers live in
    data/ref/water_demand.json (curated, sourced) as supplementary context.
    """
    import pandas as pd

    df = pd.read_csv(NEPR_NETWORK_CSV, low_memory=False)
    cols = {
        "Supply ID": "supply_id",
        "Org Name": "org",
        "Supply name": "supply",
        "D-EH1.1 Number of residential connections": "res_connections",
        "D-EH3 Total population served": "pop_served",
        "D-EH4 Total volume of water supplied to network (m3/year)": "water_supplied_m3",
        "D-RE1 Total drinking water loss across network (m3/year)": "loss_m3",
        "D-RE2.1 Current annual real loss - CARL (m3/year)": "carl_m3_year",
        "D-RE3 Infrastructure leakage index - ILI": "ili",
        "D-RE4 Median residential water consumption (L/connection/day)": "median_res_l_conn_day",
    }
    keep = [c for c in cols if c in df.columns]
    sub = df[keep].copy()
    sub = sub.rename(columns=cols)
    for c in ("res_connections", "pop_served", "water_supplied_m3", "loss_m3",
              "carl_m3_year", "ili", "median_res_l_conn_day"):
        sub[c] = pd.to_numeric(sub[c], errors="coerce")
    # one row per supply: max() is safe (rows repeat the same reported values)
    sub = sub.groupby("supply_id", as_index=False).agg({c: "max" for c in sub.columns if c != "supply_id"})
    sub["region"] = sub["org"].map(ORG_REGION)
    return sub[sub["region"].notna()].to_dict("records")


def _run_sql_analyses(population_raw: dict) -> list[dict]:
    """Run each sql/ analysis against DuckDB; returns [{name, key, sql_file, rows}]."""
    import pandas as pd

    con = duckdb.connect()
    rows = _population_records(population_raw)
    if rows:
        con.register("population", pd.DataFrame(rows))
    # full NEPR 2024/25 network data (all registered supplies in the 6 regions)
    nepr = _nepr_network_rows()
    if nepr:
        con.register("nepr_network", pd.DataFrame(nepr))
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
