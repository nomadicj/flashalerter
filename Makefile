# use some sensible default shell settings
SHELL := /bin/bash
$(VERBOSE).SILENT:

.PHONY: init
init:
	pip install -r requirements.txt

.PHONY: lint
lint:
	pylint src/

.PHONY: test
test:
	py.test tests

.PHONY: build
build:
	docker build -t flashalerter:latest .

.PHONY: scan
scan:
	docker scan flashalerter:latest

.PHONY: push
push:
	docker tag flashalerter:latest nomadicj/flashalerter:beta
	docker push nomadicj/flashalerter:beta

.PHONY: deploy
deploy:
	docker-compose up --force-recreate

.PHONY: local
local:
	python3 src/main.py

.PHONY: dockerised
dockerised:
	docker-compose up --build
	
