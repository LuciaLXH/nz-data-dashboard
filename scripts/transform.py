"""Build versioned datasets from snapshots; production and examples share this path."""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import duckdb

from nepr import FIELDS, PERIOD, normalize_networks
from flow_policy import FLOW_POLICY, register_flow_policy

ROOT = Path(__file__).resolve().parent.parent
SQL_OUTPUTS = [
    ("01_region_population_growth.sql", "population_growth"),
    ("02_supply_per_capita.sql", "supply_per_capita"),
    ("03_flow_percentile.sql", "flow_percentile"),
]
REGION_ORDER = ["auckland", "waikato", "hawkes_bay", "canterbury", "otago", "southland"]

# Operator grouping only; no claim of exact network service geography.
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

NEPR_NETWORK_CSV = ROOT / "data/raw/taumata_nepr/NEPM Final Data Extract for Release 27072026 DW_Network.csv"


def _load(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _flow_snapshot() -> dict:
    folder = ROOT / "data/raw/flow"
    snapshots = {}
    for council in ("hbrc", "orc"):
        files = sorted((folder / council).glob("[0-9]*.json"))
        if files:
            snapshots[council] = _load(files[-1])
    if not snapshots:
        raise ValueError("No flow snapshots. Fetch data or use make offline.")
    return {
        "schema_version": 1,
        "source": "council Hilltop servers (docs/W1-data-sources.md)",
        "fetched_utc": max(v["fetched_utc"] for v in snapshots.values()),
        "councils": snapshots, "status": _load(folder / "_status.json", {}),
    }


def _population_records(raw_pop: dict) -> list[dict]:
    rows, seen = [], set()
    for region, years in raw_pop.get("regions", {}).items():
        if region not in REGION_ORDER:
            raise ValueError(f"Unknown population region: {region}")
        for year, values in years.items():
            key = (region, int(year))
            pop = values.get("POP")
            if key in seen or not isinstance(pop, (int, float)) or not math.isfinite(pop) or pop <= 0:
                raise ValueError(f"Duplicate or invalid population record: {key}")
            seen.add(key)
            rows.append({"region": region, "year": int(year), "pop": pop})
    if not rows:
        raise ValueError("No population observations. Fetch data or use make offline.")
    return rows


def _flow_rows(flow: dict) -> tuple[list[dict], dict]:
    rows, seen, excluded = [], set(), []
    for council, info in flow.get("councils", {}).items():
        for site in info.get("sites", []):
            if site.get("units") not in ("m3/s", "cumecs (m3/s)"):
                raise ValueError(f"Unsupported flow units for {site.get('site')}")
            for day, value in site.get("series", []):
                key = (council, site["site"], day)
                date.fromisoformat(day)
                if key in seen:
                    raise ValueError(f"Duplicate daily flow: {key}")
                seen.add(key)
                if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    excluded.append({"council": council, "site": site["site"], "date": day,
                                     "reason": "non-numeric, non-finite or negative flow"})
                    continue
                rows.append({"council": council, "site": site["site"], "date": day,
                             "flow": value, "units": site["units"]})
    if not rows:
        raise ValueError("No usable flow observations")
    return rows, {"excluded_observations": excluded, "usable_observations": len(rows),
                  "policy": "Raw observations retained; invalid values excluded from percentile analysis, never replaced with zero."}


def run_analyses(population: list[dict], flow: list[dict], networks: list[dict],
                 as_of: date, horizon_years: int = 5) -> dict:
    # Explicit types keep an all-missing numeric column numeric, even in small examples.
    with duckdb.connect() as con:
        con.execute("CREATE TABLE population(region VARCHAR, year INTEGER, pop DOUBLE)")
        con.executemany("INSERT INTO population VALUES (?, ?, ?)",
                        [(r["region"], r["year"], r["pop"]) for r in population])
        con.execute("CREATE TABLE flow(council VARCHAR, site VARCHAR, date DATE, flow DOUBLE, units VARCHAR)")
        con.executemany("INSERT INTO flow VALUES (?, ?, ?, ?, ?)",
                        [(r["council"], r["site"], r["date"], r["flow"], r["units"]) for r in flow])
        cols = ["network_key", "region", "private_loss_boundary", *FIELDS]
        con.execute("CREATE TABLE nepr_network(" + ", ".join(
            f"{c} {'VARCHAR' if c in cols[:3] else 'DOUBLE'}" for c in cols) + ")")
        if networks:
            con.executemany("INSERT INTO nepr_network VALUES (" + ",".join("?" for _ in cols) + ")",
                            [[r[c] for c in cols] for r in networks])
        con.execute("CREATE TABLE build_context(as_of_date DATE, period_days INTEGER, scenario_horizon_years INTEGER)")
        con.execute("INSERT INTO build_context VALUES (?, ?, ?)", [as_of, PERIOD["period_days"], horizon_years])
        register_flow_policy(con)
        output = {}
        for sql, name in SQL_OUTPUTS:
            cursor = con.execute((ROOT / "sql" / sql).read_text())
            columns = [d[0] for d in cursor.description]
            output[name] = [{c: (v.isoformat() if isinstance(v, (date, datetime)) else v)
                             for c, v in zip(columns, row)} for row in cursor.fetchall()]
        return output


def build(output_dir: Path, population_raw: dict, flow: dict, nepr_path: Path = NEPR_NETWORK_CSV,
          *, input_mode: str = "snapshot", processed_utc: str | None = None,
          population_status: dict | None = None) -> dict:
    now = processed_utc or datetime.now(timezone.utc).isoformat()
    as_of = datetime.fromisoformat(now.replace("Z", "+00:00")).date()
    pop_rows = _population_records(population_raw)
    flow_rows, flow_quality = _flow_rows(flow)
    networks = normalize_networks(nepr_path, ORG_REGION)
    analyses = run_analyses(pop_rows, flow_rows, networks["rows"], as_of)
    common = {"processed_utc": now, "input_mode": input_mode}
    datasets = {
        "flow": {**flow, **common, "quality": flow_quality},
        "regions": {"schema_version": 1, "source": "data/ref/region_map.json", **common,
                    "regions": _load(ROOT / "data/ref/region_map.json")["regions"]},
        "population": {"schema_version": 1, **common, "data": population_raw,
                       "status": population_status or {"ok": True, "note": "provided snapshot"}},
        "network_records": {**networks, **common},
    }
    for sql, name in SQL_OUTPUTS:
        datasets[name] = {"schema_version": 2,
                          "sql": "sql/" + sql, **common, "rows": analyses[name]}
    datasets["supply_per_capita"].update({
        **PERIOD, "calculation_version": "network-comparison-v2",
        "geography": "operator_region_proxy", "default_loss_boundary": "No",
        "source_file": networks["source_file"], "source_sha256": networks["source_sha256"],
        "source_audit": networks["audit"]["counts"],
        "scenario_assumption": "Regional population at the stated base year uses reported network supply/person; historical CAGR continues for five years. Transfers are not reconciled.",
    })
    datasets["flow_percentile"].update({
        "quality": flow_quality, "policy": FLOW_POLICY,
        "council_snapshot_fetched_utc": {c: v["fetched_utc"] for c, v in flow["councils"].items()},
    })
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in datasets.items():
        (output_dir / (name + ".json")).write_text(
            json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return datasets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "data/processed")
    args = parser.parse_args()
    pop_files = sorted((ROOT / "data/raw/population").glob("[0-9]*.json"))
    if not pop_files:
        raise ValueError("No population snapshot. Fetch data or use make offline.")
    datasets = build(args.out, _load(pop_files[-1]), _flow_snapshot(),
                     population_status=_load(ROOT / "data/raw/population/_status.json", {"ok": False}))
    print(f"transform: schema v2 water/population; {len(datasets['network_records']['rows'])} candidate networks; "
          f"{len(datasets['supply_per_capita']['rows'])} regional comparisons → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
