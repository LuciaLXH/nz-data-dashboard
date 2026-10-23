"""Normalize NEPR records using the audited identity rules; never fill gaps."""
from __future__ import annotations

from collections import defaultdict
import hashlib
from pathlib import Path

from audit_nepr import FIELDS, IDENTITY, PRIVATE, audit_rows, number, read_csv

PERIOD = {"source_period": "2024/25", "period_start": "2024-07-01",
          "period_end": "2025-06-30", "period_days": 365, "source_release": "2026-07-27"}


def normalize_networks(path: Path, mapping: dict[str, str]) -> dict:
    raw = read_csv(path)
    required = set(IDENTITY) | set(FIELDS.values()) | {PRIVATE}
    if not raw or not required.issubset(raw[0]):
        raise ValueError(f"NEPR extract missing required columns: {sorted(required - set(raw[0] if raw else {}))}")
    accounts = defaultdict(set)
    for row in raw:
        if row.get("Account ID") and row.get("Org Name"):
            accounts[row["Account ID"]].add(row["Org Name"])
    ambiguous = {a: sorted(names) for a, names in accounts.items()
                 if len(names) > 1 and any(n in mapping for n in names)}
    if ambiguous:
        raise ValueError(f"Account ID maps to multiple organizations: {ambiguous}")

    audit = audit_rows(raw, mapping)
    repeats = {c["records"][0]["csv_record"]: [r["csv_record"] for r in c["records"]]
               for c in audit["repeated_keys_consistent_for_reviewed_fields"]}
    rows = []
    for record in audit["candidate_record_numbers"]:
        source = raw[record - 2]
        values = {name: number(source.get(col)) for name, col in FIELDS.items()}
        issues = [f"{'missing' if not source.get(col, '').strip() else 'invalid'}:{name}"
                  for name, col in FIELDS.items() if values[name] is None]
        boundary = source[PRIVATE] if source[PRIVATE] in ("No", "Yes") else "unknown"
        if boundary == "unknown":
            issues.append("unknown_private_loss_boundary")
        supply, loss = values["supply_m3_year"], values["loss_m3_year"]
        if supply == 0:
            issues.append("zero_supply_denominator")
        if supply is not None and loss is not None and loss > supply:
            issues.append("loss_above_supply")
        if values["population_served"] == 0:
            issues.append("zero_population_denominator")
        rows.append({
            "network_key": f"{PERIOD['source_release']}|{source['Account ID']}|{source['Supply ID']}",
            "account_id": source["Account ID"], "supply_id": source["Supply ID"],
            "organization": source["Org Name"], "supply_name": source["Supply name"],
            "region": mapping[source["Org Name"]], "private_loss_boundary": boundary,
            "source_file": path.name, "source_records": repeats.get(record, [record]),
            **values, "issues": issues,
            "raw_values": {name: source[col] for name, col in FIELDS.items()},
            "quality_context": {k: v for k, v in source.items() if
                "confidence" in k.lower() or "Reason not available" in k or k == PRIVATE},
        })
    return {
        "schema_version": 2, **PERIOD,
        "source_file": path.name, "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "geography": "operator_region_proxy", "rows": rows, "audit": audit,
    }
