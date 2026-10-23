"""Synthetic cases distinguish ratio-of-totals, paired denominators and boundaries."""
from datetime import date
import pytest
from nepr import FIELDS
from transform import run_analyses


def network(key,supply,loss,pop=100,boundary='No'):
    return {**dict.fromkeys(FIELDS), 'network_key':key,'region':'southland',
            'private_loss_boundary':boundary,'supply_m3_year':supply,
            'loss_m3_year':loss,'population_served':pop}


def analyse(networks,years=range(2020,2026)):
    return run_analyses([{'region':'southland','year':y,'pop':100000*1.02**(y-2020)} for y in years],
        [{'council':'orc','site':'synthetic','date':'2026-01-01','flow':1,'units':'m3/s'}],
        networks,date(2026,10,22))


def test_rate_is_ratio_of_sums_not_population_weighted_mean():
    r=analyse([network('a',36500,3650),network('b',109500,54750)])['supply_per_capita'][0]
    assert r['paired_loss_pct']==40  # (3650+54750)/(36500+109500), NOT (10+50)/2
    assert r['supply_l_person_day']==2000
    assert r['reported_supply_m3_day']==400


def test_missing_zero_excess_and_private_boundaries_have_separate_denominators():
    r=analyse([network('a',36500,3650),network('supply-only',36500,None),
               network('loss-only',None,10000),network('zero',0,0),network('excess',100,101),
               network('private',36500,18250,boundary='Yes'),
               network('unknown',36500,7300,boundary='unknown')])['supply_per_capita'][0]
    assert r['paired_loss_pct']==10
    assert r['paired_networks']==1
    assert r['supply_population_networks']==6
    assert r['supply_population_served_people']==600  # exclude loss-only population
    cohorts={c['boundary']:c for c in r['loss_cohorts']}
    assert cohorts['No']['reported_loss_m3_year']==13751 # zero, loss-only, excessive retained here
    assert cohorts['No']['paired_loss_m3_year']==3650
    assert cohorts['No']['paired_network_coverage_pct']==pytest.approx(100/7)
    assert cohorts['Yes']['paired_loss_pct']==50
    assert cohorts['unknown']['paired_loss_pct']==20


def test_empty_comparable_cohort_is_null_not_zero():
    r=analyse([network('a',36500,0,boundary='Yes')])['supply_per_capita'][0]
    assert r['paired_loss_pct'] is None
    assert r['paired_networks']==0
    assert next(c for c in r['loss_cohorts'] if c['boundary']=='Yes')['paired_loss_pct']==0


def test_all_missing_and_no_networks_remain_null():
    for networks in ([network('missing',None,None)],[]):
        r=analyse(networks)['supply_per_capita'][0]
        assert r['reported_supply_m3_year'] is None
        assert r['supply_l_person_day'] is None
        assert r['scenario_projected_supply_m3_day'] is None


def test_calendar_gaps_do_not_become_previous_year_or_five_year_growth():
    result=analyse([],years=[2019,2020,2021,2022,2024,2025])
    rows={r['year']:r for r in result['population_growth']}
    assert rows[2024]['yoy_growth_pct'] is None
    assert rows[2025]['cagr5_pct'] is None
    assert result['supply_per_capita'][0]['scenario_growth_pct'] is None


def test_new_population_year_updates_base_target_and_cagr():
    r=analyse([network('a',36500,3650)],years=range(2021,2027))['supply_per_capita'][0]
    assert (r['population_base_year'],r['projection_year'],r['cagr_start_year'],r['cagr_end_year'])==(2026,2031,2021,2026)
    assert r['cagr5_pct']==pytest.approx(2)
    assert r['scenario_growth_pct']==pytest.approx(100*(1.02**5-1))
