# to suppress the path translation in Windows
export MSYS_NO_PATHCONV=1

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
# tweak some config to avoid port conflicts
DOCKER_COMPOSE_TEST=COMPOSE_PROJECT_NAME=test_taxonomy NEO4J_ADMIN_EXPOSE=127.0.0.1:7475 NEO4J_BOLT_EXPOSE=127.0.0.1:7688 docker-compose --env-file=${ENV_FILE}

.PHONY: tests

#------------#
# dev setup  #
#------------#

build:
	@echo "🍜 Building docker images"
	${DOCKER_COMPOSE} build
	@echo "🍜 Project setup done"

up:
	@echo "🍜 Running project (ctrl+C to stop)"
	${DOCKER_COMPOSE} up

dev: build up


#-----------#
# dev tools #
#-----------#


# lint code
lint: backend_lint frontend_lint

backend_lint:
	@echo "🍜 Linting python code"
	${DOCKER_COMPOSE} run --rm taxonomy_api isort .
	${DOCKER_COMPOSE} run --rm taxonomy_api black .

frontend_lint:
	@echo "🍜 Linting react code"
	${DOCKER_COMPOSE} run --rm taxonomy_node npx prettier -w src/


# check code quality
quality: backend_quality frontend_quality

backend_quality:
	@echo "🍜 Quality checks python"
	${DOCKER_COMPOSE} run --rm taxonomy_api flake8 .
	${DOCKER_COMPOSE} run --rm taxonomy_api isort --check-only .
	${DOCKER_COMPOSE} run --rm taxonomy_api black --check .

frontend_quality:
	@echo "🍜 Quality checks JS"
	${DOCKER_COMPOSE} run --rm taxonomy_node npx prettier -c src/
	${DOCKER_COMPOSE} run --rm -e CI=true taxonomy_node npm run build
# restore the .empty file (if possible)
	git checkout taxonomy-editor-frontend/build/.empty || true



tests: backend_tests

backend_tests:
	@echo "🍜 Running python tests"
	${DOCKER_COMPOSE_TEST} up -d neo4j
	${DOCKER_COMPOSE_TEST}  run --rm taxonomy_api pytest /parser /parser
	${DOCKER_COMPOSE_TEST}  run --rm taxonomy_api pytest /code/tests
	${DOCKER_COMPOSE_TEST} stop neo4j

checks: quality tests


#------------#
# production #
#------------#

create_external_volumes:
	@echo "🍜 Creating external volumes (production only) …"
	docker volume create ${COMPOSE_PROJECT_NAME}_neo4j-data
