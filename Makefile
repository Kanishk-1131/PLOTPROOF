.PHONY: help build up down restart logs test test-unit test-integration test-security test-e2e lint clean migrate seed demo

help:
	@echo "======================================================================="
	@echo "                      PLOTPROOF SYSTEM CLI                             "
	@echo "======================================================================="
	@echo "  make build             - Build all Docker container images"
	@echo "  make up                - Start the entire system in background"
	@echo "  make down              - Stop all running containers"
	@echo "  make restart           - Restart all containers"
	@echo "  make logs              - Stream logs from all services"
	@echo "  make test              - Run all 50+ master tests across all categories"
	@echo "  make test-unit         - Run Layer 12 Unit test suite"
	@echo "  make test-integration  - Run Layer 12 Integration test suite"
	@echo "  make test-security     - Run Layer 12 Security & RBAC test suite"
	@echo "  make test-e2e          - Run Layer 12/13 End-to-End verification suite"
	@echo "  make migrate           - Apply Alembic database migrations"
	@echo "  make seed              - Pre-seed cadastral parcels and test deeds"
	@echo "  make demo              - Run controlled 3-stage judge demonstration"
	@echo "======================================================================="

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

test:
	python -m unittest discover -s tests -p "test_*.py"

test-unit:
	python -m unittest discover -s tests/unit -p "test_*.py"

test-integration:
	python -m unittest discover -s tests/integration -p "test_*.py"

test-security:
	python -m unittest discover -s tests/security -p "test_*.py"

test-e2e:
	python -m unittest discover -s tests/e2e -p "test_*.py"

lint:
	cd frontend && npm run lint

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -c "from app.seed_data.seed_db import seed_database; seed_database()"

demo:
	python -m unittest tests.e2e.test_complete_verification -v
