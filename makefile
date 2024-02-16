# ==============================================================================
# This makefile is inspired by https://github.com/ardanlabs/service
#
# Brew package manager is required for this to run
# Please follow instructions at https://docs.brew.sh/Installation

# ==============================================================================
# Define dependencies

GOLANG          := golang:1.22
PYTHON          := python:3.11-alpine3.19
ALPINE          := alpine:3.19
KIND            := kindest/node:v1.29.0@sha256:eaa1450915475849a73a9227b8f201df25e55e268e5d619312131292e324d570
POSTGRES        := postgres:16.1
GRAFANA         := grafana/grafana:10.2.0
PROMETHEUS      := prom/prometheus:v2.48.0
TEMPO           := grafana/tempo:2.3.0
LOKI            := grafana/loki:2.9.0
PROMTAIL        := grafana/promtail:2.9.0

KIND_CLUSTER    := snet
NAMESPACE       := snet
APP_FRONT       := front-p
BASE_IMAGE_NAME := vladnf/snet
SERVICE_NAME    := snet-api
VERSION         := 0.0.1
SERVICE_IMAGE   := $(BASE_IMAGE_NAME)/$(SERVICE_NAME):$(VERSION)
METRICS_IMAGE   := $(BASE_IMAGE_NAME)/$(SERVICE_NAME)-metrics:$(VERSION)
MIGRATE_IMAGE   := $(BASE_IMAGE_NAME)/$(SERVICE_NAME)-migrate:$(VERSION)
LOAD_AGENT_IMAGE   := $(BASE_IMAGE_NAME)/$(SERVICE_NAME)-load-agent:$(VERSION)

# VERSION       := "0.0.1-$(shell git rev-parse --short HEAD)"

# ==============================================================================
# Install dependencies

brew:
	brew update
	brew list kind || brew install kind
	brew list kubectl || brew install kubectl
	brew list kustomize || brew install kustomize
	brew list pgcli || brew install pgcli

pull-images:
	docker pull $(GOLANG)
	docker pull $(PYTHON)
	docker pull $(ALPINE)
	docker pull $(KIND)
	docker pull $(POSTGRES)
	docker pull $(GRAFANA)
	docker pull $(PROMETHEUS)
	docker pull $(TEMPO)
	docker pull $(LOKI)
	docker pull $(PROMTAIL)


# ==============================================================================
# Building containers

build-images: service metrics migration

service:
	docker build \
		-f infra/docker/Dockerfile.front.p \
		-t $(SERVICE_IMAGE) \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.

metrics:
	echo "Not implemented yet"

migration:
	docker build \
		-f infra/docker/Dockerfile.migrate \
		-t $(MIGRATE_IMAGE) \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.

# ==============================================================================
# Running from within k8s/kind

k8s-up: pull-images
	kind create cluster \
		--image $(KIND) \
		--name $(KIND_CLUSTER) \
		--config infra/k8s/kind-config.yaml

	kubectl wait --timeout=120s --namespace=local-path-storage --for=condition=Available deployment/local-path-provisioner

	kind load docker-image $(POSTGRES) --name $(KIND_CLUSTER)
	kind load docker-image $(GRAFANA) --name $(KIND_CLUSTER)
	kind load docker-image $(PROMETHEUS) --name $(KIND_CLUSTER)
	kind load docker-image $(TEMPO) --name $(KIND_CLUSTER)
	kind load docker-image $(LOKI) --name $(KIND_CLUSTER)
	kind load docker-image $(PROMTAIL) --name $(KIND_CLUSTER)

k8s-down:
	kind delete cluster --name $(KIND_CLUSTER)

k8s-status:
	kubectl get nodes -o wide
	kubectl get svc -o wide
	kubectl get pods -o wide --watch --all-namespaces

# ------------------------------------------------------------------------------

app-load:
	kind load docker-image $(SERVICE_IMAGE) --name $(KIND_CLUSTER)
#	kind load docker-image $(METRICS_IMAGE) --name $(KIND_CLUSTER)
	kind load docker-image $(MIGRATE_IMAGE) --name $(KIND_CLUSTER)

app-apply:
	kustomize build infra/k8s/pg-db | kubectl apply -f -
	kubectl rollout status --namespace=$(NAMESPACE) --watch --timeout=60s sts/db

	kustomize build infra/k8s/db-migrate | kubectl apply -f -
	kubectl wait jobs --namespace=$(NAMESPACE) --selector app=db-migration-job  --timeout=30s --for=condition=complete

	kustomize build infra/k8s/front | kubectl apply -f -
	kubectl wait pods --namespace=$(NAMESPACE) --selector app=$(APP_FRONT) --timeout=30s --for=condition=Ready

app-restart:
	kubectl rollout restart deployment $(APP_FRONT) --namespace=$(NAMESPACE)

update: build-images app-load app-restart

update-apply: build-images app-load app-apply

app-logs:
	kubectl logs --namespace=$(NAMESPACE) -l app=front-p --all-containers=true -f --tail=100 --max-log-requests=6
