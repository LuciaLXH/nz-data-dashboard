"""W1-minimal validation: sanity checks on data/processed/* + run record.

Writes data/processed/_runs.jsonl (one line per run; the W3 Data Health panel
expands this with null rates / schema version / 20-run colour bars).

W1 checks (record-only, graceful — see engineering decision "缺失率仅记录不硬失败"):
  - flow: ≥1 council with data, ≥1 site, ≥1 point
  - regions: 6 councils present
  - population: status file present (may be ok=false while ADE is down)
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone


def _check(checks: list[tuple[str, bool]]) -> tuple[int, int]:
    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print(f"  {'✅' if ok else '⚠️'} {name}")
    return passed, len(checks)


def main() -> int:
    os.makedirs("data/processed", exist_ok=True)
    flow = json.load(open("data/processed/flow.json", encoding="utf-8"))
    regions = json.load(open("data/processed/regions.json", encoding="utf-8"))
    population = json.load(open("data/processed/population.json", encoding="utf-8"))

    n_sites = sum(len(v.get("sites", [])) for v in flow.get("councils", {}).values())
    n_points = sum(s.get("n_points", 0) for s in flow.get("status", {}).values())
    checks = [
        ("flow: at least one council with data", bool(flow.get("councils"))),
        ("flow: at least one site", n_sites >= 1),
        ("flow: at least one point", n_points >= 1),
        ("regions: 6 councils mapped", len(regions.get("regions", [])) == 6),
        ("population: status recorded (may be degraded)", "status" in population),
    ]
    passed, total = _check(checks)
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
