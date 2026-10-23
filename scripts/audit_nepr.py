"""Reproduce the stage-one NEPR source audit without APIs or third-party packages.

The CLI reproduces the historical stage-one diagnostic without changing inputs.
Its audit_rows identity rules are also reused by the v2 production normalizer.
The report scope text records implementation status at stage-one audit time.
CSV record numbers include the header as record 1 (not physical line numbers).
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data/raw/taumata_nepr"
PREFIX = "NEPM Final Data Extract for Release 27072026 "
FIELDS = {
    "population_served": "D-EH3 Total population served",
    "supply_m3_year": "D-EH4 Total volume of water supplied to network (m3/year)",
    "loss_m3_year": "D-RE1 Total drinking water loss across network (m3/year)",
    "residential_connections": "D-EH1.1 Number of residential connections",
    "nonresidential_connections": "D-EH2.1 Number of non-residential connections",
    "nonresidential_use_m3_year": "D-EH7 Volume of non-residential water use (m3/year)",
    "carl_m3_year": "D-RE2.1 Current annual real loss - CARL (m3/year)",
    "uarl_m3_year": "D-RE2.2 Unavoidable annual real losses - UARL (m3/year)",
    "ili": "D-RE3 Infrastructure leakage index - ILI",
    "residential_median_l_connection_day": "D-RE4 Median residential water consumption (L/connection/day)",
}
PRIVATE = "D-RE1 Includes private water loss?"
IDENTITY = ("Account ID", "Org Name", "Supply ID", "Supply name")


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_mapping() -> dict[str, str]:
    # Read the existing literal, without importing transform or running its IO.
    tree = ast.parse((ROOT / "scripts/transform.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "ORG_REGION" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError("ORG_REGION literal not found; update the audit's mapping reader")


def number(value: str | None) -> float | None:
    try:
        n = float(value)
        return n if math.isfinite(n) and n >= 0 else None
    except (ValueError, TypeError):
        return None


def identify(record: int, row: dict) -> dict:
    return {"csv_record": record, **{k: row.get(k, "") for k in IDENTITY}}


def audit_rows(rows: list[dict], mapping: dict[str, str]) -> dict:
    selected = [(i, r) for i, r in enumerate(rows, 2) if r.get("Org Name") in mapping]
    missing_identity, groups = [], defaultdict(list)
    for i, r in selected:
        if any(not r.get(k, "").strip() for k in IDENTITY):
            missing_identity.append(identify(i, r))
        else:
            groups[(r["Account ID"], r["Supply ID"])].append((i, r))

    # Include quality and boundary context in duplicate equivalence, not only values.
    reviewed = set(IDENTITY) | set(FIELDS.values()) | {PRIVATE}
    reviewed.update(k for r in rows for k in r if k.startswith(
        ("D-EH1", "D-EH2", "D-EH3", "D-EH4", "D-EH7", "D-RE1", "D-RE2", "D-RE3", "D-RE4")
    ))
    repeats, conflicts, eligible = [], [], []
    for key, entries in sorted(groups.items()):
        differences = sorted(k for k in reviewed if len({r.get(k, "") for _, r in entries}) > 1)
        if len(entries) > 1:
            detail = {
                "account_id": key[0], "supply_id": key[1],
                "records": [identify(i, r) for i, r in entries],
                "differing_reviewed_fields": differences,
                "other_differing_fields": sorted(k for k in entries[0][1] if k not in reviewed
                    and len({r.get(k, "") for _, r in entries}) > 1),
            }
            if differences:
                detail["values"] = [{"csv_record": i, **{name: r.get(col, "") for name, col in FIELDS.items()}}
                                    for i, r in entries]
                conflicts.append(detail)
                continue
            repeats.append(detail)
        eligible.append(entries[0])

    def cohort_stats(entries: list[tuple[int, dict]]) -> dict:
        missing, invalid = {}, {}
        for name, col in FIELDS.items():
            missing[name] = sum(not r.get(col, "").strip() for _, r in entries)
            invalid[name] = sum(bool(r.get(col, "").strip()) and number(r.get(col)) is None
                                for _, r in entries)
        pairs, supply_only, loss_only, excessive = [], [], [], []
        for i, r in entries:
            s, loss = number(r.get(FIELDS["supply_m3_year"])), number(r.get(FIELDS["loss_m3_year"]))
            if s is not None and s > 0 and loss is not None:
                (pairs if loss <= s else excessive).append((i, r))
            elif s is not None and loss is None:
                supply_only.append(i)
            elif s is None and loss is not None:
                loss_only.append(i)
        return {
            "records": len(entries), "missing": missing, "invalid_nonblank": invalid,
            "private_loss_flags": dict(sorted(Counter(r.get(PRIVATE) or "unknown" for _, r in entries).items())),
            "paired_supply_loss_records_before_boundary_filter": len(pairs),
            "paired_records_private_loss_excluded": sum(r.get(PRIVATE) == "No" for _, r in pairs),
            "supply_without_loss_csv_records": supply_only,
            "loss_without_supply_csv_records": loss_only,
            "loss_above_supply_csv_records": [i for i, _ in excessive],
        }

    org_counts = Counter(r["Org Name"] for _, r in selected)
    return {
        "counts": {
            "source_rows": len(rows),
            "empty_template_rows": sum(not any((v or "").strip() for v in r.values()) for r in rows),
            "mapped_source_rows": len(selected),
            "mapped_organizations": len(org_counts),
            "missing_identity_rows": len(missing_identity),
            "conflicting_key_groups": len(conflicts),
            "conflicting_rows": sum(len(c["records"]) for c in conflicts),
            "consistent_repeat_rows_removed": sum(len(c["records"]) - 1 for c in repeats),
            "audit_candidate_records": len(eligible),
        },
        "missing_identity": missing_identity,
        "conflicting_keys": conflicts,
        "repeated_keys_consistent_for_reviewed_fields": repeats,
        "candidate_record_numbers": sorted(i for i, _ in eligible),
        "candidate_quality": cohort_stats(eligible),
        "candidate_quality_by_operator_region": {region: cohort_stats([
            (i, r) for i, r in eligible if mapping[r["Org Name"]] == region
        ]) for region in sorted(set(mapping.values()))},
        "organization_mapping_inventory": [{"organization": org, "region_proxy": region,
            "source_rows": org_counts[org], "geography_status": "operator grouping; service area not verified"}
            for org, region in sorted(mapping.items())],
        "unmapped_organizations_require_scope_review": sorted({r.get("Org Name") for r in rows
            if r.get("Org Name") and r["Org Name"] not in mapping}),
    }


def build_report() -> dict:
    network = SOURCE / (PREFIX + "DW_Network.csv")
    org = SOURCE / (PREFIX + "DW_Org.csv")
    dictionary = SOURCE / (PREFIX + "Data Dictionary.csv")
    mapping = read_mapping()
    result = audit_rows(read_csv(network), mapping)
    result.update({
        "audit_version": 1,
        "source_period": "2024/25", "source_release": "2026-07-27",
        "scope": "Diagnostic only; candidate exclusions are not applied by transform.py yet.",
        "sources": [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                    for p in (network, org, dictionary)],
        "mapping_source": "scripts/transform.py: ORG_REGION",
        "operator_transfers": [{"organization": r["Org Name"],
            "imports_m3_year": number(r.get("D-EH5 Water imported from other suppliers (m3/year)")),
            "exports_m3_year": number(r.get("D-EH6 Water exported to other suppliers (m3/year)"))}
            for r in read_csv(org) if r.get("Org Name") in mapping],
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the diagnostic JSON; default is stdout")
    args = parser.parse_args()
    rendered = json.dumps(build_report(), indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
