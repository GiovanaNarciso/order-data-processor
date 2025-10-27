.PHONY: test lint cov lint/test/cov run*

test:
	PYTHONPATH=. pipenv run pytest -v tests/

lint:
	flake8 app tests

cov:
	PYTHONPATH=. pipenv run pytest --cov=app --cov-report=term --cov-report=html tests/

lint/cov/test: lint cov test

install:
	pipenv install --dev

local/run:
	pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

docker/build:
	docker build -t order-normalizer-api .

docker/run:
	docker run -p 8000:8000 order-normalizer-api