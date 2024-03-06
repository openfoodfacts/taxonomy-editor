generate_spec: ## Generate swagger spec
	poetry run python -m openapi.generate_openapi_spec && cd .. && npm run lint


#------------#
# utils #
#------------#

.DEFAULT_GOAL := help

.PHONY: generate_spec help

# this command will grep targets and the following ## comment will be used as description
help: ## Description of the available commands
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)