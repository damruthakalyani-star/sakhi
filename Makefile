.PHONY: help dev dev-up dev-down test lint format build migrate backup restore clean

help:
	@echo "SAKHISAHAY Platform Developer Commands"
	@echo "---------------------------------------"
	@echo "  make dev          Run backend and frontend concurrently for local development"
	@echo "  make dev-up       Start development environment using Docker Compose"
	@echo "  make dev-down     Stop development Docker Compose containers"
	@echo "  make test         Execute backend test suite with coverage report"
	@echo "  make lint         Run Ruff linter and Black format checks"
	@echo "  make format       Auto-format codebase using Ruff and Black"
	@echo "  make build        Build production Docker images"
	@echo "  make migrate      Run database schema migrations"
	@echo "  make backup       Generate a compressed MongoDB database dump"
	@echo "  make restore      Restore MongoDB database from archive (FILE=<path>)"
	@echo "  make clean        Remove cache files, build artifacts and temporary logs"

dev-up:
	docker compose up --build -d

dev-down:
	docker compose down

test:
	cd backend && pytest tests -v --cov=app --cov-report=term-missing

lint:
	ruff check backend
	black --check backend

format:
	ruff check backend --fix
	black backend

build:
	docker compose -f docker-compose.prod.yml build

migrate:
	python scripts/migrate.py

backup:
	bash scripts/backup.sh

restore:
	@if [ -z "$(FILE)" ]; then echo "Error: specify backup file with FILE=<path>"; exit 1; fi
	bash scripts/restore.sh $(FILE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf backend/.coverage backend/coverage.xml frontend/dist
