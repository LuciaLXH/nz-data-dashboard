"""Metric units and meaningful bounds; no false population coverage ceiling."""
import pytest


def test_flow_units_and_sign(processed):
    for r in processed['flow_percentile']['rows']:
        assert r['units'] in {'m3/s','cumecs (m3/s)'}
        assert r['latest_flow_m3s'] >= 0
        assert r['n_history'] >= 0
        assert r['stale_days'] >= 0
        if r['pctile_pct'] is not None:
            assert 0 <= r['pctile_pct'] <= 100


def test_supply_units_and_bounds(processed):
    for r in processed['supply_per_capita']['rows']:
        if r['reported_supply_m3_year'] is not None:
            assert r['reported_supply_m3_day'] == pytest.approx(r['reported_supply_m3_year']/365)
        if r['supply_l_person_day'] is not None:
            assert r['supply_l_person_day'] == pytest.approx(1000*r['supply_population_supply_m3_year']/365/r['supply_population_served_people'])
        for c in r['loss_cohorts']:
            if c['paired_networks']:
                assert c['paired_loss_pct'] == pytest.approx(100*c['paired_loss_m3_year']/c['paired_supply_m3_year'])
                assert 0 <= c['paired_loss_pct'] <= 100
            else:
                assert c['paired_loss_pct'] is None
        assert r['projection_year'] == r['population_base_year']+5


def test_population_positive(processed):
    rows=processed['population_growth']['rows']
    assert all(r['pop']>0 for r in rows)
    source=processed['population']['data']['regions']
    assert {(r['region'],r['year']) for r in rows} == {(region,int(y)) for region,ys in source.items() for y in ys}
