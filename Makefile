PIP := venv/bin/pip
PYTHON := venv/bin/python

.PHONY: venv
venv: ## Create a venv to work in
	rm -rf venv
	python3 -m venv venv
	$(PIP) install -r requirements.txt

.PHONY: test
test: ## Run Python tests
	echo "test"

.PHONY: pull_mysql_docker
pull_mysql_docker: ## Pull the mysql docker from docker hub
	@docker pull mysql
