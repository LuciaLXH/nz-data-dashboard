"""Unit sanity: flows in m³/s, demand in m³/day, per-capita in L/person/day,
and physical plausibility constraints (coverage ≤ 100%, leak ≤ demand)."""


def test_flow_units_and_sign(processed):
    rows = processed["flow_percentile"]["rows"]
    assert rows, "flow_percentile should have rows"
    for r in rows:
        assert r["units"] in {"m3/s", "cumecs (m3/s)"}, r["site"]
        assert r["latest_flow_m3s"] >= 0
        assert r["n_history"] >= 0
        assert r["stale_days"] >= 0
        if r["pctile_pct"] is not None:
            assert 0 <= r["pctile_pct"] <= 100


def test_supply_units_and_bounds(processed):
    rows = processed["supply_per_capita"]["rows"]
    assert len(rows) == 6
    for r in rows:
        assert 100 <= r["l_per_person_day_w"] <= 1000, r["region"]  # L/person/day
        assert 0 <= r["loss_pct_w"] <= 100
        assert 0 <= r["coverage_pct"] <= 100
        assert 0 <= r["leak_m3_day"] <= r["daily_demand_m3"], r["region"]
        assert r["daily_demand_m3"] > 0
        assert r["proj_demand_m3_day"] > 0
        assert r["pop_served"] <= r["pop_2025"], f"{r['region']}: served > ERP"


def test_population_positive(processed):
    rows = processed["population_growth"]["rows"]
    assert len(rows) == 42  # 6 regions × 7 years
    for r in rows:
        assert r["pop"] > 0
