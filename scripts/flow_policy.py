"""Project display gate, not a hydrological standard or climatological normal."""
FLOW_POLICY = {
    'calculation_version': 'seasonal-history-v2',
    'window_radius_days': 7,
    'min_history_years': 3,
    'min_days_per_year': 10,
    'leap_day_rule': 'February 29 anchors to February 28 in non-leap years',
    'current_season': 'excluded; only windows ending before the latest observation',
    'weighting': 'pooled daily observations across all eligible prior seasonal windows',
}


def register_flow_policy(con):
    con.execute('CREATE TABLE flow_policy(window_radius_days INTEGER, min_history_years INTEGER, min_days_per_year INTEGER)')
    con.execute('INSERT INTO flow_policy VALUES (?, ?, ?)',
                [FLOW_POLICY[k] for k in ('window_radius_days','min_history_years','min_days_per_year')])
