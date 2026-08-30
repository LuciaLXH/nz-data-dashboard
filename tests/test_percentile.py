"""Percentile logic (sql/03): same-week window is YEAR-ALIGNED (a 2022-08-25
reading must be compared against a 2026-08-30 "current"), the latest
measurement itself is excluded, bands follow 25/75 thresholds, and <5 history
days yields 'insufficient'. Runs the real sql/03 against an inline flow table.
"""
import pandas as pd

from conftest import run_sql

# Site X: current = 2026-08-30 at 25 m3/s. History within ±7 days (shifted to
# 2026): 2021-08-25 (40), 2022-08-25 (5), 2023-08-25 (10), 2024-08-25 (20),
# 2025-08-25 (30) — 5 days, enough to avoid the 'insufficient' band.
# Outside window: 2025-01-01 (99) and 2022-08-22 (shifted 2026-08-22, 8 days
# before current — must NOT count). Same day latest (2026-08-30) excluded.
FLOW = pd.DataFrame([
    {"council": "hbrc", "site": "X", "date": d, "flow": v, "units": "m3/s"}
    for d, v in [
        ("2021-08-25", 40.0), ("2022-08-25", 5.0), ("2023-08-25", 10.0),
        ("2024-08-25", 20.0), ("2025-08-25", 30.0), ("2025-01-01", 99.0),
        ("2022-08-22", 7.0), ("2026-08-30", 25.0),   # the "current" measurement
    ]
])


def test_same_week_window_is_year_aligned():
    rows = run_sql("03_flow_percentile.sql", {"flow": FLOW})
    assert len(rows) == 1
    r = rows[0]
    # 5 history days in window (2021–2025 Aug 25); 2025-01-01 and 2022-08-22
    # excluded; current (2026-08-30) excluded.
    assert r["n_history"] == 5
    # values below current (25): 5, 10, 20 -> 3/5 = 60th percentile, 'normal'
    assert r["pctile_pct"] == 60.0
    assert r["band"] == "normal"
    assert r["latest_flow_m3s"] == 25.0


def test_low_and_high_bands():
    for value, expected_band in [(2.0, "low"), (40.0, "high")]:
        flow = FLOW.copy()
        flow.loc[flow["date"] == "2026-08-30", "flow"] = value
        rows = run_sql("03_flow_percentile.sql", {"flow": flow})
        assert rows[0]["band"] == expected_band, value


def test_insufficient_when_few_history_days():
    sparse = pd.DataFrame([
        {"council": "hbrc", "site": "Y", "date": d, "flow": v, "units": "m3/s"}
        for d, v in [("2025-08-25", 3.0), ("2026-08-30", 5.0)]
    ])
    rows = run_sql("03_flow_percentile.sql", {"flow": sparse})
    assert rows[0]["n_history"] == 1
    assert rows[0]["band"] == "insufficient"
