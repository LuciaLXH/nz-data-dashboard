"""Check coverage screening with synthetic records, not redistributed station data."""
import calendar
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "climate_audit", Path(__file__).parents[1] / "scripts/audit_climate_feasibility.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def record(year=2020, month=2, overrides=None):
    overrides = overrides or {}
    days = calendar.monthrange(year, month)[1]
    cells = [overrides.get(day, "   10   " if day <= days else "-9999   ")
             for day in range(1, 32)]
    return f"TEST0000001{year:04}{month:02}PRCP" + "".join(cells)


def test_leap_day_required_for_complete_month():
    result = module.ghcn_coverage(record())
    assert result["accepted_days"] == 29
    assert result["complete_baseline_months_jan_to_dec"][1] == 1
    missing = module.ghcn_coverage(record(overrides={29: "-9999   "}))
    assert missing["complete_baseline_months_jan_to_dec"][1] == 0


@pytest.mark.parametrize("cell", ["   10 X ", "    0P  ", "   10A  ", "    0I  "])
def test_quality_presumed_zero_and_partial_day_do_not_fill_month(cell):
    result = module.ghcn_coverage(record(overrides={1: cell}))
    assert result["accepted_days"] == 28
    assert result["complete_baseline_months_jan_to_dec"][1] == 0


def test_trace_keeps_source_zero_and_duplicate_month_fails():
    assert module.ghcn_coverage(record(overrides={1: "    0T  "}))["accepted_days"] == 29
    with pytest.raises(ValueError, match="Duplicate"):
        module.ghcn_coverage(record() + "\n" + record())


def test_truncated_record_fails():
    with pytest.raises(ValueError, match="Truncated"):
        module.ghcn_coverage(record()[:-8])


def test_era5_duplicate_or_missing_dates_fail():
    with pytest.raises(ValueError, match="dates"):
        module.era5_coverage([{"daily": {
            "time": ["1991-01-01", "1991-01-01"], "precipitation_sum": [0, 1]}}])
