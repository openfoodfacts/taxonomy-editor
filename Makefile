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

DOCKER_COMPOSE=docker compose --env-file=${ENV_FILE}
# tweak some config to avoid port conflicts
DOCKER_COMPOSE_TEST=COMPOSE_PROJECT_NAME=test_taxonomy NEO4J_ADMIN_EXPOSE=127.0.0.1:7475 NEO4J_BOLT_EXPOSE=127.0.0.1:7688 docker compose --env-file=${ENV_FILE}




#------------#
# local dev  #
#------------#

install: ## Install dependencies
	@echo "🍜 Installing dependencies"
	cd taxonomy-editor-frontend && npm install
	cd backend && poetry install
	cd parser && poetry install
	@echo "🍜 Project setup done"


local-frontend: ## Run the frontend locally
	@echo "🍜 Running frontend (ctrl+C to stop)"
	cd taxonomy-editor-frontend && REACT_APP_API_URL="http://localhost:8080/" npm start

local-backend: ## Run the backend locally
	@echo "🍜 Running backend (ctrl+C to stop)"
	cd backend && poetry run uvicorn editor.api:app --host 127.0.0.1 --port 8080 --env-file=../.env --reload

databases: ## Start the databases Docker container for local development
	@echo "🍜 Running neo4j (ctrl+C to stop)"
	${DOCKER_COMPOSE} up --build neo4j


#------------#
# dev setup  #
#------------#

build: ## Build docker images
	@echo "🍜 Building docker images"
	${DOCKER_COMPOSE} build
	@echo "🍜 Project setup done"

up: ## Run the project
	@echo "🍜 Running project (ctrl+C to stop)"
	@echo "🍜 The React app will be available on http://ui.taxonomy.localhost:8091"
	@echo "🍜 The API will be exposed on http://api.taxonomy.localhost:8091"
	@echo "🍜 The Neo4j admin console will be available on http://localhost:7474/browser/"
	${DOCKER_COMPOSE} up

dev: build up ## Build and run the project


#-----------#
# dev tools #
#-----------#


# lint code
lint: backend_lint frontend_lint ## Run all linters

backend_lint: ## Run lint on backend code
	@echo "🍜 Linting python code"
	${DOCKER_COMPOSE} run --rm taxonomy_api isort .
	${DOCKER_COMPOSE} run --rm taxonomy_api black .

frontend_lint: ## Run lint on frontend code
	@echo "🍜 Linting react code"
	${DOCKER_COMPOSE} run --rm taxonomy_node npx prettier -w src/


# check code quality
quality: backend_quality frontend_quality ## Run all quality checks

backend_quality: ## Run quality checks on backend code
	@echo "🍜 Quality checks python"
	${DOCKER_COMPOSE} run --rm taxonomy_api flake8 .
	${DOCKER_COMPOSE} run --rm taxonomy_api isort --check-only .
	${DOCKER_COMPOSE} run --rm taxonomy_api black --check .

frontend_quality: ## Run quality checks on frontend code
	@echo "🍜 Quality checks JS"
	${DOCKER_COMPOSE} run --rm taxonomy_node npx prettier -c src/
	${DOCKER_COMPOSE} run --rm -e CI=true taxonomy_node npm run build
# restore the .empty file (if possible)
	git checkout taxonomy-editor-frontend/build/.empty || true



tests: backend_tests ## Run all tests

backend_tests: ## Run python tests
	@echo "🍜 Running python tests"
	${DOCKER_COMPOSE_TEST} up -d neo4j
	${DOCKER_COMPOSE_TEST}  run --rm taxonomy_api pytest /parser /parser
	${DOCKER_COMPOSE_TEST}  run --rm taxonomy_api pytest /code/tests
	${DOCKER_COMPOSE_TEST} stop neo4j

checks: quality tests ## Run all checks (quality + tests)


#------------#
# production #
#------------#

create_external_volumes: ## Create external volumes (production only)
	@echo "🍜 Creating external volumes (production only) …"
	docker volume create ${COMPOSE_PROJECT_NAME}_neo4j-data


#------------#
# utils #
#------------#

.DEFAULT_GOAL := help

.PHONY: build up dev lint backend_lint frontend_lint quality backend_quality frontend_quality tests backend_tests checks create_external_volumes help

# this command will grep targets and the following ## comment will be used as description
help: ## Description of the available commands
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)