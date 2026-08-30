PYTHON ?= python3
# Prefer the project venv (has duckdb etc.) when present.
ifneq ("$(wildcard .venv/bin/python)","")
PYTHON := .venv/bin/python
endif

.PHONY: all data site test serve clean

all: data site            ## fetch → transform → validate → build site

data:                     ## run the full extract/transform/validate pipeline
	$(PYTHON) scripts/fetch_population.py
	$(PYTHON) scripts/fetch_hilltop.py
	$(PYTHON) scripts/transform.py
	$(PYTHON) scripts/validate.py

site: data                ## build the static site into site/ (W2)
	mkdir -p site/data
	cp data/processed/*.json data/processed/*.jsonl site/data/
	cp data/ref/boundaries_regions_simple.geojson site/data/boundaries.geojson
	cp data/ref/flow_sites.json data/ref/water_consents.json site/data/
	@echo "site: built into site/ — run 'make serve' to preview"

test:                     ## pytest: schema, units, region names, DST, nulls
	$(PYTHON) -m pytest -q

serve:                    ## preview locally
	$(PYTHON) -m http.server -d site 8000

clean:
	rm -rf data/processed data/raw/tmp
