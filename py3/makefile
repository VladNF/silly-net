test: up
	-pytest

test-cov: up
	-pytest --cov

build:
	docker-compose build

up:
	docker-compose up -d && docker-compose stop app

up-all: build
	docker-compose up -d

down:
	-docker-compose down --remove-orphans

update-deps:
	poetry export --with dev -o vendor/dev.txt --without-hashes
	poetry export -o vendor/prod.txt --without-hashes

gen-views:
	fastapi-codegen -i api/openapi.yaml -o app/views -t api/templates

.PHONY: up-all
