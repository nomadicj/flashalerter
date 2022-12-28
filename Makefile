# use some sensible default shell settings
SHELL := /bin/bash
$(VERBOSE).SILENT:

.PHONY: init
init:
	pip install -r requirements.txt

.PHONY: test
test:
	py.test tests

.PHONY: local
local:
	python3 src/main.py

.PHONY: dockerised
dockerised:
	docker-compose up --build
	
