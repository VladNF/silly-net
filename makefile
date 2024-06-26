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
PG-EXPORTER     := quay.io/prometheuscommunity/postgres-exporter:v0.15.0
NODE-EXPORTER   := quay.io/prometheus/node-exporter:v1.7.0
POD-EXPORTER    := registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.11.0
CADVISOR    	:= gcr.io/cadvisor/cadvisor:v0.45.0

KIND_CLUSTER    := snet
NAMESPACE       := snet
APP_FRONT       := front-p
APP_LOAD_AGENT  := load-agent
BASE_IMAGE_NAME := vladnf/snet
SERVICE_NAME    := snet-api
VERSION         := 0.0.1
SERVICE_IMAGE   := $(BASE_IMAGE_NAME)/$(SERVICE_NAME):$(VERSION)
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
	docker pull $(PG-EXPORTER)
	docker pull $(NODE-EXPORTER)
	docker pull $(POD-EXPORTER)
	docker pull $(CADVISOR)


# ==============================================================================
# Building containers

build-images: service migration load-agent

service:
	docker build \
		-f infra/docker/Dockerfile.front.p \
		-t $(SERVICE_IMAGE) \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.

migration:
	docker build \
		-f infra/docker/Dockerfile.migrate \
		-t $(MIGRATE_IMAGE) \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
		.

load-agent:
	docker build \
		-f infra/docker/Dockerfile.locust \
		-t $(LOAD_AGENT_IMAGE) \
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
	kind load docker-image $(PG-EXPORTER) --name $(KIND_CLUSTER)
	kind load docker-image $(NODE-EXPORTER) --name $(KIND_CLUSTER)
	kind load docker-image $(POD-EXPORTER) --name $(KIND_CLUSTER)
	kind load docker-image $(CADVISOR) --name $(KIND_CLUSTER)

k8s-down:
	kind delete cluster --name $(KIND_CLUSTER)

k8s-status:
	kubectl get nodes -o wide
	kubectl get svc -o wide
	kubectl get pods -o wide --watch --all-namespaces

# ------------------------------------------------------------------------------

app-load: build-images
	kind load docker-image $(SERVICE_IMAGE) --name $(KIND_CLUSTER)
	kind load docker-image $(MIGRATE_IMAGE) --name $(KIND_CLUSTER)
	kind load docker-image $(LOAD_AGENT_IMAGE) --name $(KIND_CLUSTER)

app-apply:
	kustomize build infra/k8s/grafana | kubectl apply -f -
	kustomize build infra/k8s/prometheus | kubectl apply -f -
	kustomize build infra/k8s/tempo | kubectl apply -f -
	kustomize build infra/k8s/loki | kubectl apply -f -
	kustomize build infra/k8s/promtail | kubectl apply -f -
	kustomize build infra/k8s/prom-exporters | kubectl apply -f -

	kustomize build infra/k8s/pg-db | kubectl apply -f -
	kubectl rollout status --namespace=$(NAMESPACE) --watch --timeout=60s sts/db

	kustomize build infra/k8s/front | kubectl apply -f -
	kubectl wait pods --namespace=$(NAMESPACE) --selector app=$(APP_FRONT) --timeout=30s --for=condition=Ready

	kustomize build infra/k8s/load-agent | kubectl apply -f -
	kubectl wait pods --namespace=$(NAMESPACE) --selector app=$(APP_LOAD_AGENT) --timeout=30s --for=condition=Ready

app-migrate:
	-kubectl delete job db-migration-job -n snet
	kustomize build infra/k8s/db-migrate | kubectl apply -f -
	kubectl wait jobs --namespace=$(NAMESPACE) --selector app=db-migration-job  --timeout=300s --for=condition=complete
	kubectl logs jobs/db-migration-job -n snet

app-rollback:
	@echo "DB Revision: $(db-revision)"
	-kubectl delete job db-rollback-job -n snet
	kustomize build infra/k8s/db-rollback | ROLLBACK_REVISION=$(db-revision) envsubst | kubectl apply -f -
	kubectl wait jobs --namespace=$(NAMESPACE) --selector app=db-rollback-job  --timeout=300s --for=condition=complete
	kubectl logs jobs/db-rollback-job -n snet

app-restart-front:
	kubectl rollout restart deployment $(APP_FRONT) --namespace=$(NAMESPACE)

update: build-images app-load app-restart

update-apply: build-images app-load app-apply

app-logs:
	kubectl logs --namespace=$(NAMESPACE) -l app=front-p --all-containers=true -f --tail=100 --max-log-requests=6
