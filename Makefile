# include .env
# export

DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available rules:"
	@fgrep -h "##" Makefile | fgrep -v fgrep | sed 's/\(.*\):.*##/\1:  /'

.PHONY: build
build:  ## Build the virtual environment
	@if [ ! -f .env ]; then \
	echo "Copying env_tmpl to .env ..."; \
	cp env_tmpl .env; \
	fi
	-rm -rf .venv
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

.PHONY: format
format: .venv  ## Format files
	.venv/bin/ruff format main.py

.PHONY: lint
lint: .venv  ## Lint files
	.venv/bin/ruff check main.py
