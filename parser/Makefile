.PHONY: tests

# lint code
lint:
	isort .
	black .

# check code quality
quality:
	flake8 .
	isort --check-only .
	black --check .

tests:
	pytest .

checks: quality tests