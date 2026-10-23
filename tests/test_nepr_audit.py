"""Source-audit regressions; no generated dashboard files or API keys needed."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("audit_nepr", ROOT / "scripts/audit_nepr.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def row(supply="A", volume="100", loss="10", **extra):
    return {"Account ID": "ORG", "Org Name": "Council", "Supply ID": supply,
            "Supply name": supply, audit.FIELDS["supply_m3_year"]: volume,
            audit.FIELDS["loss_m3_year"]: loss, audit.PRIVATE: "No", **extra}


def test_conflicts_are_excluded_instead_of_combining_maxima():
    result = audit.audit_rows([row(), row(volume="200", loss="5")], {"Council": "region"})
    assert result["counts"]["conflicting_key_groups"] == 1
    assert result["candidate_record_numbers"] == []


def test_quality_boundary_is_part_of_duplicate_equivalence():
    result = audit.audit_rows([row(), row(**{audit.PRIVATE: "Yes"})], {"Council": "region"})
    assert result["counts"]["conflicting_rows"] == 2


def test_unrelated_repetition_does_not_double_count_and_missing_ids_stay_visible():
    result = audit.audit_rows([row(note="one"), row(note="two"), row(supply="")], {"Council": "region"})
    assert result["candidate_record_numbers"] == [2]
    assert result["counts"]["consistent_repeat_rows_removed"] == 1
    assert result["missing_identity"][0]["csv_record"] == 4


def test_missing_zero_invalid_and_noncomparable_losses_are_distinct():
    result = audit.audit_rows([
        row("zero", loss="0"), row("missing", loss=""), row("invalid", loss="NaN"),
        row("excess", loss="101"), row("private", **{audit.PRIVATE: "Yes"}),
        row("no-supply", volume=""),
    ], {"Council": "region"})["candidate_quality"]
    assert result["missing"]["loss_m3_year"] == 1
    assert result["invalid_nonblank"]["loss_m3_year"] == 1
    assert result["paired_supply_loss_records_before_boundary_filter"] == 2
    assert result["paired_records_private_loss_excluded"] == 1
    assert result["loss_above_supply_csv_records"] == [5]
    assert result["loss_without_supply_csv_records"] == [7]


def test_pinned_source_anomalies_remain_explicit():
    result = audit.build_report()
    assert result["counts"]["mapped_source_rows"] == 272
    assert [c["supply_id"] for c in result["conflicting_keys"]] == ["OTO001"]
    assert [c["supply_id"] for c in result["repeated_keys_consistent_for_reviewed_fields"]] == ["RIV001"]
    assert result["missing_identity"][0]["Supply name"] == "Albury"
    assert result["counts"]["audit_candidate_records"] == 268
