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
	cd .. && docker-compose up -d neo4j
	pytest .
# we do not shutdown neo4j

checks: quality tests