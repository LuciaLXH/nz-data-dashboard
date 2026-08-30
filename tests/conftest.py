"""Shared fixtures for the W3 test suite.

Design: unit / region / schema tests read the real data/processed/*.json
(skipped when absent, e.g. before `make data`); SQL-logic tests (percentile,
missing-value propagation) run the ACTUAL sql/ files against small inline
tables via DuckDB — hermetic and offline, no fixtures needed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import duckdb
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
SCHEMAS = ROOT / "schemas"
SQL = ROOT / "sql"

DATASETS = {
    "flow": "flow.json",
    "regions": "regions.json",
    "population": "population.json",
    "population_growth": "population_growth.json",
    "supply_per_capita": "supply_per_capita.json",
    "flow_percentile": "flow_percentile.json",
}


def load_processed(name: str) -> dict:
    """Load one processed dataset; pytest.skip if it has not been built."""
    path = PROCESSED / DATASETS[name]
    if not path.exists():
        pytest.skip(f"data/processed/{DATASETS[name]} not built — run `make data` first")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def processed() -> dict[str, dict]:
    return {name: load_processed(name) for name in DATASETS}


def run_sql(sql_file: str, tables: dict[str, pd.DataFrame]) -> list[dict]:
    """Execute one sql/ file against DuckDB with the given tables.

    Mirrors scripts/transform.py: registers DataFrames, runs the SQL, returns
    rows as dicts (dates → ISO strings).
    """
    con = duckdb.connect()
    for name, df in tables.items():
        con.register(name, df)
    sql = (SQL / sql_file).read_text(encoding="utf-8")
    rel = con.execute(sql)
    cols = [d[0] for d in rel.description]
    rows = [
        {c: (v.isoformat() if hasattr(v, "isoformat") else v) for c, v in zip(cols, r)}
        for r in rel.fetchall()
    ]
    con.close()
    return rows
