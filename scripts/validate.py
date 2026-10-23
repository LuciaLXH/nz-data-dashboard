"""Validate versioned outputs and reconcile water metrics to network contributions."""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

from validate_flow import flow_reconciliation_errors

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ('flow', 'regions', 'population', 'population_growth', 'supply_per_capita',
            'flow_percentile', 'network_records')


def _same(actual, expected):
    return actual is None if expected is None else (
        isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-8))


def _total(rows, field):
    values = [r[field] for r in rows if r[field] is not None]
    return sum(values) if values else None


def reconciliation_errors(data: dict) -> list[str]:
    errors = []
    networks = data['network_records']['rows']
    supply = data['supply_per_capita']
    days = supply['period_days']
    keys = [r['network_key'] for r in networks]
    if len(keys) != len(set(keys)):
        errors.append('duplicate normalized network key')
    if len(networks) != data['network_records']['audit']['counts']['audit_candidate_records']:
        errors.append('normalized network count differs from audit')
    if supply['source_sha256'] != data['network_records']['source_sha256']:
        errors.append('water summary and contributions refer to different sources')
    if supply['source_audit'] != data['network_records']['audit']['counts']:
        errors.append('water summary audit counts differ from network audit')
    expected_regions = {r['region'] for r in data['regions']['regions']}
    if {r['region'] for r in supply['rows']} != expected_regions:
        errors.append('water summary does not cover the six configured regions')
    for r in supply['rows']:
        group = [n for n in networks if n['region'] == r['region']]
        pp = [n for n in group if n['supply_m3_year'] is not None and (n['population_served'] or 0) > 0]
        def check(field, expected, actual=r):
            if not _same(actual.get(field), expected):
                errors.append(f"{r['region']}: {field} does not reconcile ({actual.get(field)} vs {expected})")
        check('candidate_networks', len(group))
        check('reported_supply_networks', sum(n['supply_m3_year'] is not None for n in group))
        s = _total(group, 'supply_m3_year')
        check('reported_supply_m3_year', s)
        check('reported_supply_m3_day', s / days if s is not None else None)
        ps, pop = _total(pp, 'supply_m3_year'), _total(pp, 'population_served')
        check('supply_population_networks', len(pp))
        check('supply_population_supply_m3_year', ps)
        check('supply_population_served_people', pop)
        check('supply_l_person_day', 1000 * ps / days / pop if pop else None)
        check('supply_population_network_coverage_pct', 100 * len(pp) / len(group) if group else None)
        check('supply_population_supply_coverage_pct', 100 * ps / s if s and ps is not None else None)
        for field in ('supply', 'loss'):
            check(f'missing_or_invalid_{field}_networks', sum(n[f'{field}_m3_year'] is None for n in group))
        excessive = lambda n: n['supply_m3_year'] is not None and n['loss_m3_year'] is not None and n['loss_m3_year'] > n['supply_m3_year']
        check('loss_above_supply_networks', sum(excessive(n) for n in group))
        cohorts = {c['boundary']: c for c in r['loss_cohorts']}
        if set(cohorts) != {'No', 'Yes', 'unknown'}:
            errors.append(f"{r['region']}: missing or repeated loss boundary")
            continue
        for boundary, cohort in cohorts.items():
            bg = [n for n in group if n['private_loss_boundary'] == boundary]
            pairs = [n for n in bg if (n['supply_m3_year'] or 0) > 0 and n['loss_m3_year'] is not None and n['loss_m3_year'] <= n['supply_m3_year']]
            volume, loss = _total(pairs, 'supply_m3_year'), _total(pairs, 'loss_m3_year')
            expected = {'boundary_candidate_networks':len(bg), 'reported_loss_networks':sum(n['loss_m3_year'] is not None for n in bg),
                        'reported_loss_m3_year':_total(bg,'loss_m3_year'), 'paired_networks':len(pairs),
                        'paired_supply_m3_year':volume, 'paired_loss_m3_year':loss,
                        'paired_loss_pct':100 * loss / volume if volume else None,
                        'paired_network_coverage_pct':100 * len(pairs) / len(group) if group else None,
                        'paired_supply_coverage_pct':100 * volume / s if s and volume is not None else None,
                        'loss_above_supply_networks':sum(excessive(n) for n in bg)}
            for field, value in expected.items():
                check(field, value, cohort)
        for field in ('paired_loss_pct', 'paired_networks', 'paired_supply_coverage_pct'):
            check(field, cohorts['No'][field])
        years = data['population']['data']['regions'][r['region']]
        latest = max(map(int, years))
        check('population_base_year', latest)
        check('population_base', years[str(latest)]['POP'])
        check('projection_year', latest + r['scenario_horizon_years'])
        check('cagr_start_year', latest - 5)
        check('cagr_end_year', latest)
        complete = all(str(y) in years for y in range(latest-5, latest+1))
        cagr = (years[str(latest)]['POP'] / years[str(latest-5)]['POP']) ** (1/5) - 1 if complete else None
        check('cagr5_pct', cagr * 100 if cagr is not None else None)
        factor = (1+cagr)**r['scenario_horizon_years'] if cagr is not None else None
        check('scenario_growth_pct', 100 * (factor-1) if factor is not None else None)
        base = r['population_base'] * r['supply_l_person_day'] / 1000 if r['supply_l_person_day'] is not None else None
        check('scenario_base_supply_m3_day', base)
        check('scenario_projected_supply_m3_day', base * factor if base is not None and factor is not None else None)
    return errors


def validate(output_dir: Path, *, write_log: bool = True) -> dict:
    data, checks, errors = {}, [], []
    for name in DATASETS:
        try:
            data[name] = json.loads((output_dir / f'{name}.json').read_text())
            schema = json.loads((ROOT / 'schemas' / f'{name}.schema.json').read_text())
            jsonschema.validate(data[name], schema, format_checker=jsonschema.FormatChecker())
            checks.append((name + ': schema', True))
        except (FileNotFoundError, ValueError, jsonschema.ValidationError) as exc:
            checks.append((name + ': schema', False))
            errors.append(f'{name}: {exc}')
    if all(ok for _, ok in checks):
        errors.extend(reconciliation_errors(data))
        checks.append(('water: reconcile to network contributions and population years', not errors))
        flow_errors=flow_reconciliation_errors(data)
        errors.extend(flow_errors)
        checks.append(('flow: calendar windows, coverage and ranks reconcile to daily sources', not flow_errors))
        checks.append(('flow: at least one usable monitored site', bool(data['flow_percentile']['rows'])))
        expected = {(region,int(year)) for region, ys in data['population']['data']['regions'].items() for year in ys}
        actual = [(r['region'],r['year']) for r in data['population_growth']['rows']]
        checks.append(('population: one analysis row per source observation', len(actual)==len(set(actual)) and set(actual)==expected))
    passed = sum(ok for _,ok in checks)
    flow, population = data.get('flow',{}), data.get('population',{})
    def null_pct(name, fields):
        rows = data.get(name,{}).get('rows',[])
        return {f:round(100 * sum(r.get(f) is None for r in rows)/len(rows),1) if rows else None for f in fields}
    run = {'utc': datetime.now(timezone.utc).isoformat(), 'schema_version':2,
           'input_mode':data.get('supply_per_capita',{}).get('input_mode'),
           'checks_passed':passed,'checks_total':len(checks),
           'flow_degraded_councils':[c for c,v in flow.get('status',{}).items() if not v.get('ok')],
           'population_ok':population.get('status',{}).get('ok',False),
           'flow_excluded_observations':len(flow.get('quality',{}).get('excluded_observations',[])),
           'rows':{**{n+'_rows':len(data.get(n,{}).get('rows',[])) for n in ('supply_per_capita','population_growth','flow_percentile','network_records')},
                   'population_region_years':sum(len(ys) for ys in population.get('data',{}).get('regions',{}).values())},
           'null_pct':{'supply_per_capita':null_pct('supply_per_capita',['supply_l_person_day','paired_loss_pct']),
                       'flow_percentile':null_pct('flow_percentile',['pctile_pct'])}}
    if write_log:
        output_dir.mkdir(parents=True,exist_ok=True)
        with (output_dir/'_runs.jsonl').open('a') as f:
            f.write(json.dumps(run)+'\n')
    if passed != len(checks):
        raise ValueError('Validation failed: ' + '; '.join(errors + [name for name,ok in checks if not ok]))
    return run


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dir',type=Path,default=ROOT/'data/processed')
    args=parser.parse_args()
    run=validate(args.dir)
    print(f"validate: {run['checks_passed']}/{run['checks_total']} checks passed; contributions reconciled → {args.dir}")


if __name__=='__main__':
    main()
