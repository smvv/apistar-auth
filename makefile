all:

test:
	pipenv run pytest -q --tb=short

lint:
	pipenv run prospector

coverage:
	pipenv run pytest -q --cov-report=term --cov-report=html --cov=apistar_auth

watch:
	pipenv run ptw -q --clear -- -q --tb=short
