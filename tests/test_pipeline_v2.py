"""Integration checks against pinned source evidence and reproducible builds."""
from copy import deepcopy
import hashlib
import json
import socket

import pytest
from build_offline import build_example, FIXTURES
from nepr import normalize_networks
from transform import ORG_REGION, NEPR_NETWORK_CSV, _flow_rows
from validate import reconciliation_errors, validate
from audit_nepr import read_csv


@pytest.fixture(scope='module')
def normalized():
    return normalize_networks(NEPR_NETWORK_CSV,ORG_REGION)


def test_loader_applies_audited_identity_decisions(normalized):
    rows=normalized['rows']
    assert len(rows)==268
    assert not any(r['supply_id']=='OTO001' or r['supply_name']=='Albury' for r in rows)
    riv=[r for r in rows if r['supply_id']=='RIV001']
    assert len(riv)==1
    assert riv[0]['source_records']==[406,407]
    assert normalized['audit']['counts']['conflicting_rows']==2
    assert normalized['audit']['counts']['missing_identity_rows']==1
    assert sum('invalid:nonresidential_connections' in r['issues'] for r in rows)==3
    assert sum('loss_above_supply' in r['issues'] for r in rows)==2
    assert sum('zero_supply_denominator' in r['issues'] for r in rows)==3


def test_pinned_comparable_coverage_is_not_all_networks(normalized):
    expected={'auckland':(25,10),'canterbury':(97,63),'hawkes_bay':(19,10),
              'otago':(45,19),'southland':(15,0),'waikato':(67,35)}
    for region,(candidates,pairs) in expected.items():
        rows=[r for r in normalized['rows'] if r['region']==region]
        valid=[r for r in rows if r['private_loss_boundary']=='No' and
               (r['supply_m3_year'] or 0)>0 and r['loss_m3_year'] is not None and r['loss_m3_year']<=r['supply_m3_year']]
        assert (len(rows),len(valid))==(candidates,pairs)


def test_normalized_values_preserve_raw_evidence(normalized):
    for r in normalized['rows']:
        for field,raw in r['raw_values'].items():
            if r[field] is not None:
                assert float(raw)==r[field]
            else:
                assert f'missing:{field}' in r['issues'] or f'invalid:{field}' in r['issues']


def test_water_fixture_matches_attributed_original_records():
    manifest=json.loads((FIXTURES/'MANIFEST.json').read_text())
    assert hashlib.sha256(NEPR_NETWORK_CSV.read_bytes()).hexdigest()==manifest['network']['sha256']
    original,excerpt=read_csv(NEPR_NETWORK_CSV),read_csv(FIXTURES/'networks.csv')
    for ref in manifest['network']['record_mapping']:
        assert excerpt[ref['fixture_csv_record']-2]==original[ref['original_csv_record']-2]


def test_reconciliation_detects_changed_rate_and_denominator(processed):
    assert reconciliation_errors(processed)==[]
    for field in ['paired_loss_pct','supply_population_served_people','reported_supply_m3_year','projection_year']:
        changed=deepcopy(processed)
        row=next(r for r in changed['supply_per_capita']['rows'] if r[field] is not None)
        row[field]+=1
        assert any(field in error for error in reconciliation_errors(changed))


def test_offline_build_has_no_fetch_and_is_deterministic(tmp_path,monkeypatch):
    import requests
    import transform
    def no_network(*args,**kwargs):
        pytest.fail('Offline build attempted source access')
    monkeypatch.setattr(socket,'create_connection',no_network)
    monkeypatch.setattr(requests.Session,'request',no_network)
    monkeypatch.setattr(transform,'_flow_snapshot',no_network)
    a=build_example(tmp_path/'one'); b=build_example(tmp_path/'two')
    assert a==b
    assert a['supply_per_capita']['input_mode']=='offline_example'
    assert a['network_records']['example_provenance']['network']['record_mapping']
    assert len(a['network_records']['rows'])==37 # 41 source rows minus 2 conflicts, missing ID, repeated water row
    assert validate(tmp_path/'one',write_log=False)['checks_passed']==11
    (tmp_path/'one/supply_per_capita.json').unlink()
    with pytest.raises(ValueError,match='Validation failed'):
        validate(tmp_path/'one',write_log=False)


def test_flow_negative_observations_remain_raw_but_not_analysed():
    source={'councils':{'orc':{'sites':[{'site':'synthetic','units':'m3/s','series':[['2020-01-01',-1],['2020-01-02',0]]}]}}}
    rows,quality=_flow_rows(source)
    assert len(rows)==1 and rows[0]['flow']==0
    assert quality['excluded_observations'][0]['date']=='2020-01-01'
    assert source['councils']['orc']['sites'][0]['series'][0][1]==-1
    source['councils']['orc']['sites'][0]['series'].append(['2020-01-02',3])
    with pytest.raises(ValueError,match='Duplicate daily flow'):
        _flow_rows(source)


def test_flow_reconciliation_catches_window_counts_and_unsupported_rank(processed):
    from validate_flow import flow_reconciliation_errors
    assert flow_reconciliation_errors(processed)==[]
    changed=deepcopy(processed)
    changed['flow_percentile']['rows'][0]['n_history']+=1
    assert any('n_history' in e for e in flow_reconciliation_errors(changed))
    changed=deepcopy(processed)
    changed['flow_percentile']['rows'][0]['n_qualified_years']+=1
    assert any('n_qualified_years' in e for e in flow_reconciliation_errors(changed))
    changed=deepcopy(processed)
    row=changed['flow_percentile']['rows'][0]
    row['pctile_pct']=50 if row['pctile_pct'] is None else None
    assert any('pctile_pct' in e for e in flow_reconciliation_errors(changed))
