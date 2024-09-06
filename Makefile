# include .env
# export

DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available rules:"
	@fgrep -h "##" Makefile | fgrep -v fgrep | sed 's/\(.*\):.*##/\1:  /'

.PHONY: format
format:  ## Format files
	uvx ruff format build_report.py

.PHONY: lint
lint:  ## Lint files
	uvx ruff check build_report.py
