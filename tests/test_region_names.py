"""Region-name integrity: 6 councils, official REGC codes, boundaries join."""
import json

import pytest

from conftest import ROOT

EXPECTED = {
    "auckland": ("02", "Auckland"),
    "waikato": ("03", "Waikato"),
    "hawkes_bay": ("06", "Hawke's Bay"),
    "canterbury": ("13", "Canterbury"),
    "otago": ("14", "Otago"),
    "southland": ("15", "Southland"),
}


def test_region_map_has_6_official_councils(processed):
    regions = processed["regions"]["regions"]
    assert len(regions) == 6
    found = {r["region"]: (r["stats_nz"]["regec"], r["display"]["en"]) for r in regions}
    assert found == EXPECTED


def test_boundaries_join_region_map(processed):
    with open(ROOT / "data" / "ref" / "boundaries_regions_simple.geojson", encoding="utf-8") as f:
        geojson = json.load(f)
    region_keys = {r["region"] for r in processed["regions"]["regions"]}
    assert len(geojson["features"]) == 6
    for feat in geojson["features"]:
        assert feat["properties"]["region"] in region_keys
        assert feat["geometry"]["type"] == "Polygon"


@pytest.mark.parametrize("dataset", ["population_growth", "supply_per_capita"])
def test_analysis_rows_reference_known_regions(processed, dataset):
    region_keys = {r["region"] for r in processed["regions"]["regions"]}
    for r in processed[dataset]["rows"]:
        assert r["region"] in region_keys
