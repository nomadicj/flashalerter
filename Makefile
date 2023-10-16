# use some sensible default shell settings
SHELL := /bin/bash
$(VERBOSE).SILENT:

# DOCKER_LOGIN := docker login -u $DOCKER_USER -p $DOCKER_PASS
DOCKER_LOGIN := cat /etc/buildkite/docker-config.txt | docker login --username nomadicj --password-stdin
DOCKER_PUSH := docker push nomadicj/flashalerter:beta

.PHONY: init
init:
	pip install -r requirements.txt

.PHONY: lint
lint:
	pylint src/

.PHONY: test
test:
	src/py.test tests

.PHONY: build
build:
	docker build -t flashalerter:latest .

.PHONY: scan
scan:
	docker scan flashalerter:latest

.PHONY: push
push:
	docker tag flashalerter:latest nomadicj/flashalerter:beta
	$(DOCKER_PUSH) || ($(DOCKER_LOGIN) && $(DOCKER_PUSH))

.PHONY: deploy
deploy:
	docker-compose up --force-recreate

.PHONY: local
local:
	python3 src/main.py

.PHONY: dockerised
dockerised:
	docker-compose up --force-recreate
