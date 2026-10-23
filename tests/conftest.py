"""Core checks always execute: build examples unless an explicit output is supplied."""
import json
import os
import sys
from pathlib import Path

import duckdb
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / 'schemas'
SQL = ROOT / 'sql'
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import DATASETS as DATASET_NAMES
from flow_policy import register_flow_policy
DATASETS = {name: name+'.json' for name in DATASET_NAMES}


@pytest.fixture(scope='session')
def processed_dir(tmp_path_factory):
    configured = os.getenv('DASHBOARD_PROCESSED_DIR')
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else ROOT/path
    from build_offline import build_example
    path = tmp_path_factory.mktemp('offline-processed')
    build_example(path)
    return path


@pytest.fixture(scope='session')
def processed(processed_dir):
    # Missing outputs are errors, never skipped checks.
    return {name:json.loads((processed_dir/file).read_text()) for name,file in DATASETS.items()}


def run_sql(sql_file: str, tables: dict[str,pd.DataFrame]) -> list[dict]:
    with duckdb.connect() as con:
        for name, df in tables.items():
            con.register(name,df)
        if 'build_context' not in tables:
            con.execute("CREATE TABLE build_context AS SELECT DATE '2026-10-22' AS as_of_date, 365 AS period_days, 5 AS scenario_horizon_years")
        register_flow_policy(con)
        rel=con.execute((SQL/sql_file).read_text())
        cols=[d[0] for d in rel.description]
        return [{c:(v.isoformat() if hasattr(v,'isoformat') else v) for c,v in zip(cols,row)} for row in rel.fetchall()]
