ENVS := $(shell cat .env)

test: up
	-pytest

test-cov: up
	-pytest --cov

build:
	docker-compose build

up:
	docker-compose up -d

down:
	-docker-compose down --remove-orphans

update-deps:
	poetry export --with dev -o vendor/dev.txt --without-hashes
	poetry export -o vendor/prod.txt --without-hashes

gen-views:
	fastapi-codegen -i api/http.yaml -o app/views -t api/templates

db-migrate:
	@$(ENVS) yoyo apply

db-recreate:
	@$(ENVS) yoyo develop

new-migration:
	@$(ENVS) yoyo new --sql

new-migration-python:
	@$(ENVS) yoyo new

list-migrations:
	@$(ENVS) yoyo list

import-people:
	@$(ENVS) python -m tests.import

run-locust:
	@$(ENVS) locust -f tests/load.py

.PHONY: up
