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


local_frontend: ## Run the frontend locally
	@echo "🍜 Running frontend (ctrl+C to stop)"
	cd taxonomy-editor-frontend && REACT_APP_API_URL="http://localhost:8080/" npm start

local_backend: ## Run the backend locally
	@echo "🍜 Running backend (ctrl+C to stop)"
	cd backend && poetry run uvicorn editor.api:app --host 127.0.0.1 --port 8080 --env-file=../.env --reload

databases: ## Start the databases Docker container for local development
	@echo "🍜 Running neo4j (ctrl+C to stop)"
	${DOCKER_COMPOSE} up --build neo4j

add_local_test_data: ## Add test data to the local database
	@echo "🍜 Adding test data to the database"
	cd backend && poetry run python sample/load.py sample/test-neo4j.json

local_lint: local_backend_lint local_frontend_lint local_config_lint ## Run lint on local code

local_backend_lint: ## Run lint on local backend code
	@echo "🍜 Linting python code"
	cd backend && poetry run isort --skip .venv .
	cd backend && poetry run black --exclude=.venv .

local_frontend_lint: ## Run lint on local frontend code
	@echo "🍜 Linting react code"
	cd taxonomy-editor-frontend && npm run lint

local_config_lint: ## Run on lint configuration files
	@echo "🍜 Linting configuration files"
	npm run lint


local_quality: local_backend_quality local_frontend_quality local_config_quality ## Run lint on local code

local_backend_quality: ## Run lint on local backend code
	@echo "🍜 Quality python code checks"
	cd backend && poetry run isort --check-only --skip .venv .
	cd backend && poetry run black --check --exclude=.venv .
	cd backend && poetry run flake8 --exclude=.venv .

local_frontend_quality: ## Run lint on local frontend code
	@echo "🍜 Quality react code checks"
	cd taxonomy-editor-frontend && npm run lint:check

local_config_quality: ## Run on lint configuration files
	@echo "🍜 Quality configuration files checks"
	npm run lint:check

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
lint: backend_lint frontend_lint config_lint ## Run all linters

backend_lint: ## Run lint on backend code
	@echo "🍜 Linting python code"
	${DOCKER_COMPOSE} run --rm taxonomy_api isort .
	${DOCKER_COMPOSE} run --rm taxonomy_api black .

frontend_lint: ## Run lint on frontend code
	@echo "🍜 Linting react code"
	${DOCKER_COMPOSE} run --rm taxonomy_node npx eslint --fix src/
	${DOCKER_COMPOSE} run --rm taxonomy_node npx prettier -w src/

config_lint: ## Run on lint configuration files
	@echo "🍜 Linting configuration files"
	${DOCKER_COMPOSE} run --rm taxonomy_editor_code npm run lint


# check code quality
quality: backend_quality frontend_quality config_quality ## Run all quality checks

backend_quality: ## Run quality checks on backend code
	@echo "🍜 Quality checks python"
	${DOCKER_COMPOSE} run --rm taxonomy_api flake8 --exclude=.venv .
	${DOCKER_COMPOSE} run --rm taxonomy_api isort --check-only --skip .venv .
	${DOCKER_COMPOSE} run --rm taxonomy_api black --check --exclude=.venv .

frontend_quality: ## Run quality checks on frontend code
	@echo "🍜 Quality checks JS"
	${DOCKER_COMPOSE} run --rm taxonomy_node npx eslint --no-fix src/
	${DOCKER_COMPOSE} run --rm taxonomy_node npx prettier -c src/
	${DOCKER_COMPOSE} run --rm -e CI=true taxonomy_node npm run build
# restore the .empty file (if possible)
	git checkout taxonomy-editor-frontend/build/.empty || true

config_quality: ## Run quality checks on configuration files
	@echo "🍜 Quality checks configuration files"
	${DOCKER_COMPOSE} run --rm taxonomy_editor_code npm run lint:check


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