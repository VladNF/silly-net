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
	export $(cat .env | xargs) && yoyo apply

db-recreate:
	export $(cat .env | xargs) && yoyo develop

new-migration:
	export $(cat .env | xargs) && yoyo new --sql

.PHONY: up-all
