"""W1-minimal validation: schema + sanity checks on data/processed/*.

Writes data/processed/_runs.jsonl (one line per run; the W3 Data Health panel
expands this with null rates / schema version / 20-run colour bars).

Checks (record-only, graceful — see engineering decision "缺失率仅记录不硬失败"):
  - JSON Schema (schemas/*.schema.json) for flow / regions / population
  - flow: ≥1 council with data, ≥1 site, ≥1 point
  - regions: 6 councils present
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import jsonschema

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMAS = {
    "flow": "schemas/flow.schema.json",
    "regions": "schemas/regions.schema.json",
    "population": "schemas/population.schema.json",
    "population_growth": "schemas/population_growth.schema.json",
    "supply_per_capita": "schemas/supply_per_capita.schema.json",
    "flow_percentile": "schemas/flow_percentile.schema.json",
}


def _load_schema(name: str) -> dict:
    path = os.path.join(HERE, "..", SCHEMAS[name])
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _schema_check(dataset: str, data: dict) -> tuple[bool, str]:
    try:
        jsonschema.validate(data, _load_schema(dataset))
        return True, "schema ok"
    except jsonschema.ValidationError as e:
        return False, f"schema: {e.message}"


def main() -> int:
    os.makedirs("data/processed", exist_ok=True)
    flow = json.load(open("data/processed/flow.json", encoding="utf-8"))
    regions = json.load(open("data/processed/regions.json", encoding="utf-8"))
    population = json.load(open("data/processed/population.json", encoding="utf-8"))
    try:
        growth = json.load(open("data/processed/population_growth.json", encoding="utf-8"))
    except FileNotFoundError:
        growth = {}
    try:
        supply = json.load(open("data/processed/supply_per_capita.json", encoding="utf-8"))
    except FileNotFoundError:
        supply = {}
    try:
        flow_pct = json.load(open("data/processed/flow_percentile.json", encoding="utf-8"))
    except FileNotFoundError:
        flow_pct = {}

    n_sites = sum(len(v.get("sites", [])) for v in flow.get("councils", {}).values())
    n_points = sum(s.get("n_points", 0) for s in flow.get("status", {}).values())

    flow_ok, flow_msg = _schema_check("flow", flow)
    regions_ok, regions_msg = _schema_check("regions", regions)
    pop_ok, pop_msg = _schema_check("population", population)
    growth_ok = bool(growth) and _schema_check("population_growth", growth)[0]
    growth_rows = len(growth.get("rows", [])) if growth else 0
    supply_ok = bool(supply) and _schema_check("supply_per_capita", supply)[0]
    supply_rows = len(supply.get("rows", [])) if supply else 0
    flow_pct_ok = bool(flow_pct) and _schema_check("flow_percentile", flow_pct)[0]
    flow_pct_rows = len(flow_pct.get("rows", [])) if flow_pct else 0

    checks = [
        ("flow: JSON Schema", flow_ok),
        ("flow: at least one council with data", flow_ok and bool(flow.get("councils"))),
        ("flow: at least one site", n_sites >= 1),
        ("flow: at least one point", n_points >= 1),
        ("regions: JSON Schema", regions_ok),
        ("regions: 6 councils mapped", len(regions.get("regions", [])) == 6),
        ("population: JSON Schema", pop_ok),
        ("population: status recorded (may be degraded)", "status" in population),
        ("growth: JSON Schema", growth_ok),
        ("growth: rows for all 6 regions × 7 years", growth_rows >= 6 * 7),
        ("supply: JSON Schema", supply_ok),
        ("supply: rows for all 6 regions", supply_rows >= 6),
        ("flow_percentile: JSON Schema", flow_pct_ok),
        ("flow_percentile: one row per monitored flow site (>= 11)", flow_pct_rows >= 11),
    ]
    passed, total = 0, len(checks)
    for name, ok in checks:
        passed += 1 if ok else 0
        print(f"  {'✅' if ok else '⚠️'} {name}")

    degraded = [c for c in flow.get("status", {}).values() if not c.get("ok")]
    run = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "checks_passed": passed,
        "checks_total": total,
        "flow_sites": n_sites,
        "flow_points": n_points,
        "flow_degraded_councils": [c.get("council") for c in degraded],
        "population_ok": population.get("status", {}).get("ok", False),
    }
    with open("data/processed/_runs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(run) + "\n")
    print(f"validate: {passed}/{total} checks passed → appended _runs.jsonl")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
