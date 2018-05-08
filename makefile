all:

test:
	pipenv run pytest -q --tb=short

lint:
	pipenv run prospector

coverage:
	pipenv run pytest -q --cov-report=term --cov-report=html --cov=apistar_auth

watch:
	pipenv run ptw -q --clear -- -q --tb=short

upload:
	rm -f dist/*
	python setup.py sdist
	twine upload dist/*
