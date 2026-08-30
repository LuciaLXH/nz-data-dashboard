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

site:                     ## build the static site into site/ (W2)
	@echo "TODO(W2): build ECharts + Leaflet site from data/processed/*.json"

test:                     ## pytest: schema, units, region names, DST, nulls
	$(PYTHON) -m pytest -q

serve:                    ## preview locally
	$(PYTHON) -m http.server -d site 8000

clean:
	rm -rf data/processed data/raw/tmp
