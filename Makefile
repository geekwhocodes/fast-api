.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

REGISTRY="380617998106.dkr.ecr.us-west-2.amazonaws.com/opal"
IMAGE_NAME=dopalizer


.PHONY: build
build:	## Build docker image
	docker build -f Dockerfile -t $(IMAGE_NAME) .

.PHONY: up
up:	## Run docker image
	docker run --env-file .env --rm -e MAX_WORKERS="1" -p 8000:80 "$(IMAGE_NAME)-slim"

.PHONY: push
push: ## Push images to ECR
	## docker login -u AWS -p $(aws ecr get-login-password --region us-west-2 --profile gwc) "$(REGISTRY)"
	docker tag opal "$(REGISTRY):opal"
	docker tag "$(REGISTRY):$(IMAGE_NAME)-slim"
	docker push "$(REGISTRY):$(IMAGE_NAME)"
	docker push "$(REGISTRY):$(IMAGE_NAME)-slim"

.PHONY: clean
clean: ## Clean Reset project containers
	docker rm $(docker stop $(docker ps -a -q --filter ancestor=$(IMAGE_NAME) --format="{{.ID}}")) --force
	docker rm $(docker stop $(docker ps -a -q --filter ancestor="$(IMAGE_NAME)-slim" --format="{{.ID}}")) --force

.PHONY: migrate-apply
migrate-apply: ## apply alembic migrations to database/schema
	docker-compose run --rm app alembic -x tenant="$(tenant)" upgrade head

.PHONY: migrate-create
migrate-create:  ## Create new alembic database migration aka database revision.
	docker-compose up -d db | true
	docker-compose run --no-deps app alembic revision -m "$(msg)"

.PHONY: test
test:	## Run project tests
	docker run -e "OPALIZERENV=dev" --rm $(IMAGE_NAME) poetry run pytest

.PHONY: safety
safety:	## Check project and dependencies with safety https://github.com/pyupio/safety
	docker-compose run --rm opal_api safety check

.PHONY: py-upgrade
py-upgrade:	## Upgrade project py files with pyupgrade library for python version 3.10
	pyupgrade --py311-plus `find $(IMAGE_NAME) -name "*.py"`

.PHONY: lint
lint:  ## Lint project code.
	poetry run ruff .

.PHONY: formate
format:  ## Format project code.
	black $(IMAGE_NAME) tests --line-length=120

.PHONY: slim-build
slim-build: ## with power of docker-slim build smaller and safer images
	docker-slim build --target $(IMAGE_NAME) --tag $(IMAGE_NAME)-slim --env "OPALIZERENV=dev" --env "OPALIZER_GMAPS_KEY=es"
