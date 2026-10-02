.PHONY: install data sample dbt train test app all ci

START ?= 202101

install:
	pip install -r requirements.txt && pip install -e .

data:            ## pull real EPD aggregates from the NHSBSA API
	python scripts/fetch_epd.py --start $(START)

sample:          ## synthetic data with the same schema (CI / offline)
	python scripts/make_sample_data.py

dbt:
	cd dbt && dbt build --profiles-dir .

train:
	python -m rxforecast.train

test:
	pytest -q

app:
	streamlit run app/streamlit_app.py

all: data dbt train

ci: sample dbt test train
