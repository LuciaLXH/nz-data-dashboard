"""Every output is required and checked, including normalized network records."""
import json
import jsonschema
import pytest
from conftest import SCHEMAS, DATASETS


@pytest.mark.parametrize('dataset', sorted(DATASETS))
def test_schema(dataset, processed):
    schema=json.loads((SCHEMAS/(dataset+'.schema.json')).read_text())
    jsonschema.validate(processed[dataset],schema,format_checker=jsonschema.FormatChecker())
