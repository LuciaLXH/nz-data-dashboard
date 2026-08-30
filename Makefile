.PHONY: all data site test serve clean

all: data site            ## fetch → transform → validate → build site

data:                     ## run the full extract/transform/validate pipeline
	python scripts/fetch_population.py
	python scripts/fetch_hilltop.py
	python scripts/transform.py
	python scripts/validate.py

site:                     ## build the static site into site/ (W2)
	@echo "TODO(W2): build ECharts + Leaflet site from data/processed/*.json"

test:                     ## pytest: schema, units, region names, DST, nulls
	pytest -q

serve:                    ## preview locally
	python -m http.server -d site 8000

clean:
	rm -rf data/processed data/raw/tmp
