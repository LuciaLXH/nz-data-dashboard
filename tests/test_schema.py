"""Schema validation: every processed dataset matches its JSON Schema."""
import json

import jsonschema
import pytest

from conftest import PROCESSED, SCHEMAS, DATASETS

SCHEMA_FILES = {
    "flow": "flow.schema.json",
    "regions": "regions.schema.json",
    "population": "population.schema.json",
    "population_growth": "population_growth.schema.json",
    "supply_per_capita": "supply_per_capita.schema.json",
    "flow_percentile": "flow_percentile.schema.json",
}


@pytest.mark.parametrize("dataset", sorted(DATASETS))
def test_schema(dataset: str):
    path = PROCESSED / DATASETS[dataset]
    if not path.exists():
        pytest.skip(f"data/processed/{DATASETS[dataset]} not built")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    with open(SCHEMAS / SCHEMA_FILES[dataset], encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(data, schema)  # raises ValidationError on failure
