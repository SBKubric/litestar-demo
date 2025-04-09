SHELL := /bin/bash
# =============================================================================
# Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
.EXPORT_ALL_VARIABLES:
MAKEFLAGS += --no-print-directory

# Define colors and formatting
BLUE := $(shell printf "\033[1;34m")
GREEN := $(shell printf "\033[1;32m")
RED := $(shell printf "\033[1;31m")
YELLOW := $(shell printf "\033[1;33m")
NC := $(shell printf "\033[0m")
INFO := $(shell printf "$(BLUE)ℹ$(NC)")
OK := $(shell printf "$(GREEN)✓$(NC)")
WARN := $(shell printf "$(YELLOW)⚠$(NC)")
ERROR := $(shell printf "$(RED)✖$(NC)")

.PHONY: help
help:                                               ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


# =============================================================================
# Developer Utils
# =============================================================================
.PHONY: install poetry + python
install-poetry:                                         ## Install poetry
	@echo "${INFO} Installing pyenv..."
	@curl -fsSL https://pyenv.run | bash
	@pyenv install 3.12
	@pyenv global 3.12

	@echo "${INFO} Installing poetry..."
	@pip install poetry==1.8.3
	@echo "${OK} Poetry installed successfully"

.PHONY: install
install: destroy clean                             ## Install the project, dependencies, and pre-commit for local development
	@pyenv activate litestar-demo > /dev/null 2>&1
	@echo "${INFO} Starting fresh installation..."
	@poetry install -q -n --with dev
	@echo "${OK} Installation complete! 🎉"

.PHONY: upgrade
upgrade:                                            ## Upgrade all dependencies to the latest stable versions
	@pyenv activate litestar-demo > /dev/null 2>&1
	@echo "${INFO} Updating all dependencies... 🔄"
	@poetry update
	@poetry lock
	@echo "${OK} Dependencies updated 🔄"
	@poetry run pre-commit autoupdate
	@echo "${OK} Updated Pre-commit hooks 🔄"

.PHONY: clean
clean:                                              ## Cleanup temporary build artifacts
	@echo "${INFO} Cleaning working directory..."
	@rm -rf pytest_cache .ruff_cache .hypothesis build/ -rf dist/ .eggs/ .coverage coverage.xml coverage.json htmlcov/ .pytest_cache tests/.pytest_cache tests/**/.pytest_cache .mypy_cache .unasyncd_cache/ .auto_pytabs_cache node_modules >/dev/null 2>&1
	@find . -name '*.egg-info' -exec rm -rf {} + >/dev/null 2>&1
	@find . -type f -name '*.egg' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*.pyc' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*.pyo' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*~' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '__pycache__' -exec rm -rf {} + >/dev/null 2>&1
	@find . -name '.ipynb_checkpoints' -exec rm -rf {} + >/dev/null 2>&1
	@echo "${OK} Working directory cleaned"
	$(MAKE) docs-clean

.PHONY: destroy
destroy:                                            ## Destroy the virtual environment
	@echo "${INFO} Destroying virtual environment... 🗑️"
	@rm -rf .venv
	@echo "${OK} Virtual environment destroyed 🗑️"

.PHONY: lock
lock:                                              ## Rebuild lockfiles from scratch, updating all dependencies
	@echo "${INFO} Rebuilding lockfiles... 🔄"
	@poetry lock >/dev/null 2>&1
	@echo "${OK} Lockfiles updated"


.PHONY: run
run:                                               ## Run the application in dev container
	@docker compose -f docker-compose.yml -f docker-compose.override.yml up -d



# =============================================================================
# Tests, Linting, Coverage
# =============================================================================
.PHONY: mypy
mypy:                                              ## Run mypy
	@echo "${INFO} Running mypy... 🔍"
	@poetry run dmypy run src/app
	@echo "${OK} Mypy checks passed ✨"

.PHONY: pyright
pyright:                                           ## Run pyright
	@echo "${INFO} Running pyright... 🔍"
	@poetry run pyright
	@echo "${OK} Pyright checks passed ✨"

.PHONY: type-check
type-check: mypy pyright                           ## Run all type checking

.PHONY: pre-commit
pre-commit:                                        ## Runs pre-commit hooks; includes ruff formatting and linting, codespell
	@echo "${INFO} Running pre-commit checks... 🔎"
	@poetry run pre-commit run --color=always --all-files
	@echo "${OK} Pre-commit checks passed ✨"

.PHONY: slotscheck
slotscheck:                                        ## Run slotscheck
	@echo "${INFO} Running slots check... 🔍"
	@poetry run slotscheck -m app
	@echo "${OK} Slots check passed ✨"

.PHONY: fix
fix:                                               ## Run formatting scripts
	@echo "${INFO} Running code formatters... 🔧"
	@poetry run ruff check --fix --unsafe-fixes
	@echo "${OK} Code formatting complete ✨"

.PHONY: lint
lint: pre-commit type-check slotscheck             ## Run all linting

.PHONY: coverage
coverage:                                          ## Run the tests and generate coverage report
	@echo "${INFO} Running tests with coverage... 📊"
	@poetry run pytest tests --cov -n auto --quiet
	@poetry run coverage html >/dev/null 2>&1
	@poetry run coverage xml >/dev/null 2>&1
	@echo "${OK} Coverage report generated ✨"

.PHONY: test
test:                                              ## Run the tests
	@echo "${INFO} Running test cases... 🧪"
	@poetry run pytest tests -n 2 --quiet
	@echo "${OK} Tests passed ✨"

.PHONY: test-all
test-all:                                          ## Run all tests
	@echo "${INFO} Running all test cases... 🧪"
	@poetry run pytest tests -m '' -n 2 --quiet
	@echo "${OK} All tests passed ✨"

.PHONY: check-all
check-all: lint test-all coverage                  ## Run all linting, tests, and coverage checks


# =============================================================================
# Docs
# =============================================================================
.PHONY: docs-clean
docs-clean:                                        ## Dump the existing built docs
	@echo "${INFO} Cleaning documentation build assets... 🧹"
	@rm -rf docs/_build >/dev/null 2>&1
	@echo "${OK} Documentation assets cleaned"

.PHONY: docs-serve
docs-serve: docs-clean                             ## Serve the docs locally
	@echo "${INFO} Starting documentation server... 📚"
	@poetry run sphinx-autobuild docs docs/_build/ -j auto --watch app --watch docs --watch tests --watch CONTRIBUTING.rst --port 8002

.PHONY: docs
docs: docs-clean                                   ## Dump the existing built docs and rebuild them
	@echo "${INFO} Building documentation... 📝"
	@poetry run sphinx-build -M html docs docs/_build/ -E -a -j auto -W --keep-going
	@echo "${OK} Documentation built successfully"

.PHONY: docs-linkcheck
docs-linkcheck:                                    ## Run the link check on the docs
	@echo "${INFO} Checking documentation links... 🔗"
	@poetry run sphinx-build -b linkcheck ./docs ./docs/_build -D linkcheck_ignore='http://.*','https://.*' >/dev/null 2>&1
	@echo "${OK} Link check complete"

.PHONY: docs-linkcheck-full
docs-linkcheck-full:                               ## Run the full link check on the docs
	@echo "${INFO} Running full link check... 🔗"
	@poetry run sphinx-build -b linkcheck ./docs ./docs/_build -D linkcheck_anchors=0 >/dev/null 2>&1
	@echo "${OK} Full link check complete"


# -----------------------------------------------------------------------------
# Local Infrastructure
# -----------------------------------------------------------------------------

.PHONY: start-infra
start-infra:                                        ## Start local containers
	@echo "${INFO} Starting local infrastructure... 🚀"
	@docker compose -f deploy/docker-compose.infra.yml up -d --force-recreate >/dev/null 2>&1
	@echo "${OK} Infrastructure is ready"

.PHONY: stop-infra
stop-infra:                                         ## Stop local containers
	@echo "${INFO} Stopping infrastructure... 🛑"
	@docker compose -f deploy/docker-compose.infra.yml down >/dev/null 2>&1
	@echo "${OK} Infrastructure stopped"

.PHONY: wipe-infra
wipe-infra:                                           ## Remove local container info
	@echo "${INFO} Wiping infrastructure... 🧹"
	@docker compose -f deploy/docker-compose.infra.yml down -v --remove-orphans >/dev/null 2>&1
	@echo "${OK} Infrastructure wiped clean"

.PHONY: infra-logs
infra-logs:                                           ## Tail development infrastructure logs
	@echo "${INFO} Tailing infrastructure logs... 📋"
	@docker compose -f deploy/docker-compose.infra.yml logs -f

.PHONY: start-app
start-app:                                          ## Start the app
	@echo "${INFO} Starting app... 🚀"
	@docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
	@echo "${OK} App started"

.PHONY: stop-app
stop-app:                                           ## Stop the app
	@echo "${INFO} Stopping app... 🛑"
	@docker compose -f docker-compose.yml -f docker-compose.override.yml down
	@echo "${OK} App stopped"

.PHONY: wipe-app
wipe-app:                                           ## Remove app container info
	@echo "${INFO} Wiping app... 🧹"
	@docker compose -f docker-compose.yml -f docker-compose.override.yml down -v --remove-orphans > /dev/null 2>&1
	@echo "${OK} App wiped clean"
