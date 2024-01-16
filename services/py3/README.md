# Install
```shell
cp .env.example .env
make build
docker-compose up -d db
make db-recreate
make up
```

# Tests
Use Postman collection from `tests/postmain.json`
* sign-up
* login
* search
* get

Import people' profiles `make import-people`

Run `locust` with `make run-locust`

# Shutdown
```shell
make down
```
