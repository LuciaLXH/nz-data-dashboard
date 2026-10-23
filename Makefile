PYTHON ?= python3
# Prefer the project venv (has duckdb etc.) when present.
ifneq ("$(wildcard .venv/bin/python)","")
PYTHON := .venv/bin/python
endif

.PHONY: all data site site-data test serve clean gif offline serve-offline

all: data site            ## fetch → transform → validate → build site

data:                     ## run the full extract/transform/validate pipeline
	$(PYTHON) scripts/fetch_population.py
	$(PYTHON) scripts/fetch_hilltop.py
	$(PYTHON) scripts/transform.py
	$(PYTHON) scripts/validate.py

site-data:                ## package validated data for the production site
	$(PYTHON) scripts/build_site.py

offline:                  ## build attributed examples without API keys or source fetches
	$(PYTHON) scripts/build_offline.py

serve-offline:            ## preview the example separately from production
	$(PYTHON) -m http.server -d .tmp/offline/site 8001

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
