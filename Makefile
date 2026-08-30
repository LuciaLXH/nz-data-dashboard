PYTHON ?= python3
# Prefer the project venv (has duckdb etc.) when present.
ifneq ("$(wildcard .venv/bin/python)","")
PYTHON := .venv/bin/python
endif

.PHONY: all data site site-data test serve clean gif

all: data site            ## fetch → transform → validate → build site

data:                     ## run the full extract/transform/validate pipeline
	$(PYTHON) scripts/fetch_population.py
	$(PYTHON) scripts/fetch_hilltop.py
	$(PYTHON) scripts/transform.py
	$(PYTHON) scripts/validate.py

site-data:                ## copy the files the site actually reads into site/data
	rm -rf site/data
	mkdir -p site/data
	# only the datasets consumed by site/app.js — raw flow.json (1.3 MB) and
	# population.json are W1 packaging artifacts, not used by the front end
	cp data/processed/population_growth.json data/processed/supply_per_capita.json \
	   data/processed/flow_percentile.json data/processed/regions.json \
	   data/processed/_runs.jsonl site/data/
	cp data/ref/boundaries_regions_simple.geojson site/data/boundaries.geojson
	cp data/ref/flow_sites.json data/ref/water_consents.json site/data/

site: data site-data      ## build the static site into site/ (W2)
	@echo "site: built into site/ — run 'make serve' to preview"

test:                     ## pytest: schema, units, region names, DST, nulls
	$(PYTHON) -m pytest -q

gif:                      ## re-record the 15s demo GIF (needs playwright + pillow)
	$(PYTHON) scripts/make_demo_gif.py

serve:                    ## preview locally
	$(PYTHON) -m http.server -d site 8000

clean:
	rm -rf data/processed data/raw/tmp
