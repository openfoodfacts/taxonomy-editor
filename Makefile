ifeq ($(findstring cmd.exe,$(SHELL)),cmd.exe)
    $(error "We do not suppport using cmd.exe on Windows, please run in a 'git bash' console")
endif

# use bash everywhere !
SHELL := /bin/bash
ENV_FILE ?= .env

# load env variables
# also takes into account envrc (direnv file)
ifneq (,$(wildcard ./${ENV_FILE}))
    -include ${ENV_FILE}
    -include .envrc
    export
endif

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

DOCKER_COMPOSE=docker-compose --env-file=${ENV_FILE}
DOCKER_COMPOSE_TEST=COMPOSE_PROJECT_NAME=test_taxonomy docker-compose --env-file=${ENV_FILE}

.PHONY: tests

#-----------#
# dev tools #
#-----------#

# lint code
lint: backend_lint

backend_lint:
	@echo "🍜 Linting python code"
	${DOCKER_COMPOSE} run --rm taxonomy_api isort .
	${DOCKER_COMPOSE} run --rm taxonomy_api black .

# check code quality
quality: backend_quality frontend_quality

backend_quality:
	@echo "🍜 Quality checks python"
	${DOCKER_COMPOSE} run --rm taxonomy_api flake8 .
	${DOCKER_COMPOSE} run --rm taxonomy_api isort --check-only .
	${DOCKER_COMPOSE} run --rm taxonomy_api black --check .

frontend_quality:
	@echo "🍜 Quality checks JS"
	${DOCKER_COMPOSE} run --rm -e CI=true taxonomy_node npm run build


tests: backend_tests

backend_tests:
	@echo "🍜 Running python tests"
	${DOCKER_COMPOSE_TEST} up -d neo4j
	${DOCKER_COMPOSE_TEST}  run --rm taxonomy_api pytest . /parser
	${DOCKER_COMPOSE_TEST} stop neo4j

checks: quality tests


#------------#
# production #
#------------#

create_external_volumes:
	@echo "🍜 Creating external volumes (production only) …"
	docker volume create ${COMPOSE_PROJECT_NAME}_neo4j-data

