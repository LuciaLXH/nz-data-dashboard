"""Missing-value propagation: a supply with a NULL metric must be EXCLUDED
from sql/02's population-weighted averages, not counted as zero.

Runs the real sql/02_supply_per_capita.sql against a tiny inline NEPR table
with one NULL per-capita row and asserts the weighted mean stays clean.
"""
import pandas as pd

from conftest import run_sql

POPULATION = pd.DataFrame([
    {"region": "southland", "year": y, "pop": 100000 + i}
    for i, y in enumerate(range(2020, 2026))
])

# region "southland": supply A reports water (1000 L/p/d), supply B reports
# water=NULL (e.g. a supply that did not report volume this year).
NEPR = pd.DataFrame([
    {"region": "southland", "supply_id": "A", "org": "Southland District Council",
     "supply": "A", "res_connections": 100, "pop_served": 100.0,
     "water_supplied_m3": 36500.0, "loss_m3": 3650.0, "carl_m3_year": 100.0,
     "ili": 2.0, "median_res_l_conn_day": None},
    {"region": "southland", "supply_id": "B", "org": "Southland District Council",
     "supply": "B", "res_connections": 100, "pop_served": 100.0,
     "water_supplied_m3": None, "loss_m3": None, "carl_m3_year": None,
     "ili": None, "median_res_l_conn_day": None},
])


def test_null_per_capita_excluded_from_weighted_average():
    rows = run_sql("02_supply_per_capita.sql", {"population": POPULATION, "nepr_network": NEPR})
    southland = next(r for r in rows if r["region"] == "southland")
    # supply A: 36500 m3/yr / 365 = 100 m3/day; /100 people *1000 = 1000 L/p/d.
    # If supply B's NULL were counted as 0, the mean would be 500.
    assert southland["l_per_person_day_w"] == 1000.0
    # loss: 3650/36500 = 10% (B's NULL excluded, not 0%)
    assert southland["loss_pct_w"] == 10.0
    assert southland["pop_served"] == 200.0  # pop_served itself sums fine


def test_null_does_not_crash_sql():
    rows = run_sql("02_supply_per_capita.sql", {"population": POPULATION, "nepr_network": NEPR})
    assert len(rows) == 1  # only southland in this fixture
