# Install
```shell
cp .env.example .env
make build
docker-compose up -d db
make db-recreate
make up
```

# Tests
Use Postman collection from `tests/SNet.postmain.json`
* sign-up
* login
* search
* get

# Shutdown
```shell
make down
```
