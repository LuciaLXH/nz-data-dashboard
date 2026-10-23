"""Real SQL: calendar windows, completed seasons and the multi-year display gate."""
from datetime import date, timedelta
import pandas as pd
import pytest

from conftest import run_sql

# Ten genuine date slots in each synthetic season, with known rank counts.
FLOW = pd.DataFrame([
    {"council":"hbrc", "site":"X", "date":(date(year,8,24)+timedelta(days=day)).isoformat(),
     "flow":value,"units":"m3/s"}
    for year,value in [(2021,40.),(2022,5.),(2023,10.),(2024,20.),(2025,30.)]
    for day in range(10)
] + [
    {"council":"hbrc", "site":"X", "date":day,"flow":value,"units":"m3/s"}
    for day,value in [("2025-01-01",99.),("2022-08-22",7.),("2026-08-30",25.)]
])


def test_same_week_window_is_year_aligned():
    rows = run_sql("03_flow_percentile.sql", {"flow": FLOW})
    assert len(rows) == 1
    r = rows[0]
    assert r["n_history"] == 50
    assert r["n_history_years"] == r["n_qualified_years"] == 5
    # Three of five equally sampled synthetic seasons are below the latest.
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
    assert rows[0]["pctile_pct"] is None


def percentile(observations):
    return run_sql('03_flow_percentile.sql', {'flow': pd.DataFrame([
        {'council':'hbrc','site':'synthetic calendar case','date':d,'flow':v,'units':'m3/s'}
        for d,v in observations])})[0]


def test_january_window_includes_previous_december_but_not_eighth_day():
    r=percentile([('2023-12-26',99),('2023-12-27',1),('2024-01-10',2),
                  ('2024-01-11',99),('2026-01-03',3)])
    assert r['n_history']==2
    assert r['median_hist_m3s']==1.5


def test_december_window_includes_following_january():
    # December 31 ±7 = Dec 24 through Jan 7.
    r=percentile([('2023-12-23',99),('2023-12-24',1),('2024-01-07',2),
                  ('2024-01-08',99),('2025-12-31',3)])
    assert r['n_history']==2
    assert r['median_hist_m3s']==1.5


def test_march_window_uses_calendar_dates_across_leap_years():
    r=percentile([('2023-02-21',99),('2023-02-22',1),('2023-03-08',2),
                  ('2023-03-09',99),('2024-03-01',3)])
    assert r['n_history']==2  # 2023 March 1 window, NOT 2024 day-of-year positions
    r=percentile([('2024-02-22',99),('2024-02-23',1),('2024-03-08',2),
                  ('2024-03-09',99),('2025-03-01',3)])
    assert r['n_history']==2


def test_february_29_anchor_clamps_only_in_non_leap_years():
    r=percentile([('2023-02-20',99),('2023-02-21',1),('2023-03-07',2),
                  ('2023-03-08',99),('2024-02-29',3)])
    assert r['n_history']==2
    r=percentile([('2020-02-21',99),('2020-02-22',1),('2020-03-07',2),
                  ('2020-03-08',99),('2024-02-29',3)])
    assert r['n_history']==2


def seasonal_days(year, n=10, value=1):
    return [((date(year,8,24)+timedelta(days=i)).isoformat(),value) for i in range(n)]


def test_many_days_in_one_or_two_years_cannot_pass_multi_year_gate():
    for years in [[2025],[2024,2025]]:
        r=percentile([x for year in years for x in seasonal_days(year,14)] + [('2026-08-30',2)])
        assert r['n_qualified_years']==len(years)
        assert r['pctile_pct'] is None and r['band']=='insufficient'


def test_three_sparse_years_fail_and_exact_three_dense_years_pass():
    sparse=percentile([x for year in [2023,2024,2025] for x in seasonal_days(year,9)]+[('2026-08-30',2)])
    assert sparse['n_history_years']==3 and sparse['n_qualified_years']==0
    assert sparse['pctile_pct'] is None
    enough=percentile([x for year in [2023,2024,2025] for x in seasonal_days(year,10)]+[('2026-08-30',2)])
    assert enough['n_qualified_years']==3 and enough['pctile_pct']==100
    assert enough['history_coverage_pct']==pytest.approx(100*30/45)


def test_current_partial_season_excluded_even_across_new_year():
    r=percentile([('2023-12-27',1),('2024-01-03',2),('2025-12-27',0),
                  ('2026-01-02',0),('2026-01-03',3)])
    assert r['n_history']==2
    assert r['n_history_years']==1  # December and January form one season
    assert r['history_years']==[
        {'season_year':2024,'observed_days':2,'expected_days':15,'qualifies':False},
        {'season_year':2025,'observed_days':0,'expected_days':15,'qualifies':False}]
    assert r['history_last_date']=='2024-01-03'


def test_missing_seasons_remain_in_coverage_denominator():
    r=percentile(seasonal_days(2022)+seasonal_days(2024)+seasonal_days(2025)+[('2026-08-30',2)])
    assert r['n_history_seasons']==4 and r['n_history_years']==3
    assert r['expected_history_days']==60 and r['history_coverage_pct']==50
    assert r['history_years'][1]['observed_days']==0


def test_no_completed_history_has_empty_coverage_not_zero_flow():
    r=percentile([('2026-08-29',0),('2026-08-30',2)])
    assert r['n_history']==r['n_history_seasons']==0
    assert r['history_years']==[]
    assert r['history_coverage_pct'] is None
    assert r['history_year_start'] is None and r['history_first_date'] is None
    assert r['min_hist_m3s'] is None and r['pctile_pct'] is None
    assert r['latest_flow_m3s']==2


@pytest.mark.parametrize('below,band',[(0,'low'),(10,'normal'),(30,'normal'),(31,'high')])
def test_ties_and_exact_band_boundaries(below,band):
    observations=[x for year in [2022,2023,2024,2025] for x in seasonal_days(year)]
    observations=[(d,0 if i<below else 10) for i,(d,_) in enumerate(observations)]
    r=percentile(observations+[('2026-08-30',10)])
    assert r['pctile_pct']==100*below/40
    assert r['n_below_latest']==below and r['band']==band
    assert r['min_hist_m3s']==(0 if below else 10)
