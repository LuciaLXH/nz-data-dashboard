"""Time handling: pipeline stores UTC; display converts to Pacific/Auckland
with correct NZ DST rules (NZDT = UTC+13 in summer, NZST = UTC+12 in winter).

The site converts in the browser via Intl (DST-aware). This test pins the
expected instants so the Python side and the browser agree:
  - DST ends 2026-04-05 03:00 NZDT -> 02:00 NZST  == 2026-04-04 14:00 UTC
  - DST starts 2026-09-27 02:00 NZST -> 03:00 NZDT == 2026-09-26 14:00 UTC
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

AUCKLAND = ZoneInfo("Pacific/Auckland")

DST_END_UTC = datetime(2026, 4, 4, 14, 0, tzinfo=timezone.utc)
DST_START_UTC = datetime(2026, 9, 26, 14, 0, tzinfo=timezone.utc)


def to_auckland(iso_utc: str) -> datetime:
    dt = datetime.fromisoformat(iso_utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(AUCKLAND)


def test_processed_timestamps_are_utc(processed):
    """Pipeline must store UTC (site converts for display)."""
    for name, doc in processed.items():
        ts = doc.get("processed_utc") or doc.get("fetched_utc")
        if ts:
            assert ts.endswith("+00:00") or ts.endswith("Z"), f"{name}: {ts} not UTC"


@pytest.mark.parametrize("iso_utc,expected_local", [
    # summer: NZDT = UTC+13
    ("2026-01-15T12:00:00+00:00", "2026-01-16T01:00:00+13:00"),
    # winter: NZST = UTC+12
    ("2026-06-15T12:00:00+00:00", "2026-06-16T00:00:00+12:00"),
])
def test_winter_and_summer_offsets(iso_utc, expected_local):
    local = to_auckland(iso_utc)
    assert local.isoformat() == expected_local


def test_dst_spring_forward_boundary():
    """Just before the April transition local time is still NZDT (+13)."""
    just_before = datetime(2026, 4, 4, 13, 59, tzinfo=timezone.utc).astimezone(AUCKLAND)
    assert just_before.utcoffset().total_seconds() == 13 * 3600  # still NZDT
    assert just_before.strftime("%Y-%m-%d %H:%M") == "2026-04-05 02:59"


def test_dst_autumn_back_boundary():
    """At and after the April transition local time is NZST (+12)."""
    instant = DST_END_UTC.astimezone(AUCKLAND)
    assert instant.utcoffset().total_seconds() == 12 * 3600  # NZST
    assert instant.strftime("%Y-%m-%d %H:%M") == "2026-04-05 02:00"


def test_dst_september_forward_boundary():
    """Just before Sept 27 02:00 NZST local is +12; at 02:00 it jumps to +13."""
    before = datetime(2026, 9, 26, 13, 59, tzinfo=timezone.utc).astimezone(AUCKLAND)
    assert before.utcoffset().total_seconds() == 12 * 3600
    at = DST_START_UTC.astimezone(AUCKLAND)
    assert at.utcoffset().total_seconds() == 13 * 3600  # NZDT
    assert at.strftime("%Y-%m-%d %H:%M") == "2026-09-27 03:00"
