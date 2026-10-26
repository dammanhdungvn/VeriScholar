.PHONY: setup dev verify lint test build

setup:
	bash scripts/dev/setup.sh

dev:
	bash scripts/dev/setup.sh --start

verify:
	bash scripts/dev/verify.sh

lint:
	uv run ruff check . && uv run ruff format --check .

test:
	uv run pytest && npm --prefix apps/web run test

build:
	npm --prefix apps/web run build
