"""Reconcile SQL seasonal outputs to daily observations with Python date arithmetic."""
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, timedelta
import math
from statistics import median

from flow_policy import FLOW_POLICY


def flow_reconciliation_errors(data: dict) -> list[str]:
    errors, sites = [], defaultdict(dict)
    for council, source in data['flow']['councils'].items():
        for site in source['sites']:
            for day, value in site['series']:
                if isinstance(value,(int,float)) and math.isfinite(value) and value>=0:
                    key=(council,site['site'])
                    d=date.fromisoformat(day)
                    if d in sites[key]:
                        errors.append(f'{key}: duplicate source day {day}')
                    sites[key][d]=value
    output=data['flow_percentile']
    rows=output['rows']
    if len(rows)!=len(sites) or {(r['council'],r['site']) for r in rows}!=set(sites):
        errors.append('flow output sites do not match valid daily sources')
    radius=FLOW_POLICY['window_radius_days']
    min_days=FLOW_POLICY['min_days_per_year']
    min_years=FLOW_POLICY['min_history_years']
    as_of=datetime.fromisoformat(output['processed_utc'].replace('Z','+00:00')).date()
    for row in rows:
        key=(row['council'],row['site'])
        if key not in sites:
            continue
        obs=sites[key]
        first,latest=min(obs),max(obs)
        years, history = [], {}
        for year in range(first.year-1,latest.year+1):
            centre=date(year,latest.month,min(latest.day,monthrange(year,latest.month)[1]))
            start,end=centre-timedelta(days=radius),centre+timedelta(days=radius)
            if end>=latest or end<first:
                continue
            subset={d:v for d,v in obs.items() if start<=d<=end}
            years.append({'season_year':year,'observed_days':len(subset),'expected_days':2*radius+1,
                          'qualifies':len(subset)>=min_days})
            history.update(subset)
        n=len(history)
        n_qualified=sum(y['qualifies'] for y in years)
        below=sum(v<obs[latest] for v in history.values())
        expected_days=sum(y['expected_days'] for y in years)
        pct=100*below/n if n and n_qualified>=min_years else None
        expected={'latest_date':latest.isoformat(),'latest_flow_m3s':obs[latest],
                  'n_history':n,'n_below_latest':below,
                  'n_history_seasons':len(years),'n_history_years':sum(y['observed_days']>0 for y in years),
                  'n_qualified_years':n_qualified,'expected_history_days':expected_days,
                  'history_year_start':years[0]['season_year'] if years else None,
                  'history_year_end':years[-1]['season_year'] if years else None,
                  'history_first_date':min(history).isoformat() if history else None,
                  'history_last_date':max(history).isoformat() if history else None,
                  'history_coverage_pct':100*n/expected_days if expected_days else None,
                  'history_years':years,'pctile_pct':pct,
                  'history_status':'sufficient' if pct is not None else 'insufficient_years',
                  'band':'insufficient' if pct is None else 'low' if pct<25 else 'normal' if pct<=75 else 'high',
                  'median_hist_m3s':median(history.values()) if history else None,
                  'min_hist_m3s':min(history.values()) if history else None,
                  'max_hist_m3s':max(history.values()) if history else None,
                  'stale_days':(as_of-latest).days}
        for field,value in expected.items():
            actual=row.get(field)
            equal=(isinstance(actual,(float,int)) and math.isclose(actual,value,rel_tol=1e-10,abs_tol=1e-10)) if isinstance(value,(int,float)) else actual==value
            if not equal:
                errors.append(f'{key}: {field} differs from daily-source reconciliation')
    return errors
