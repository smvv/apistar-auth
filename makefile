all:

test:
	pipenv run pytest -q --tb=short

watch:
	pipenv run ptw -q --clear -- -q --tb=short
