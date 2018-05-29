all:

test:
	pipenv run pytest -q --tb=short

db:
	docker-compose up -d

lint:
	pipenv run prospector

coverage:
	pipenv run pytest -q --cov-report=term --cov-report=html --cov=apistar_auth

watch:
	pipenv run ptw -q --clear -- -q --tb=short --maxfail 1

upload:
	rm -f dist/*
	python setup.py sdist
	twine upload dist/*
