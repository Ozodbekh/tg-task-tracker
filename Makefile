.DEFAULT_GOAL := help
.PHONY: help install hash-password login set-webhook seed run digest test lint format check clean

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

install: ## Install backend dependencies
	uv sync

hash-password: ## Print a password hash for ADMIN_PASSWORD_HASH
	uv run python -m app.core.hash_password

login: ## Sign in to Telegram and write the session file
	uv run python -m app.telegram.login

set-webhook: ## Point the Telegram bot at this server and publish its commands
	uv run python -m app.bot.setup

seed: ## Fill the database with fake rows for UI testing
	uv run python -m app.db.seed

run: ## Run the Telegram listener
	uv run python -m app.main

digest: ## Send the digest to every employee with an unfinished task
	uv run python -m app.digest

test: ## Run the test suite
	uv run pytest -q

lint: ## Check formatting and lint rules
	uv run ruff check backend
	uv run ruff format --check backend

format: ## Apply formatting and safe fixes
	uv run ruff check --fix backend
	uv run ruff format backend

check: lint test ## Run every check

clean: ## Remove caches
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache
