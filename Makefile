PIP := venv/bin/pip
PYTHON := venv/bin/python
NETWORK := la_international_speedway
DB_CONTAINER_NAME := rust_eze
DB_CONTAINER_PORT := 3306
DB_NAME := ACT
DB_USER := lightning
DB_PWD := McQueen95
PY_CONTAINER_NAME := radiator_springs
PY_IMAGE_NAME := py-dock

.PHONY: requirements.txt
requirements.txt: ## update requirements from current environment
	pip freeze > requirements.txt

.PHONY: venv
venv: ## Create a venv to work in
	rm -rf venv
	python3 -m venv venv
	$(PIP) install -r requirements.txt

.PHONY: test
test: ## Run Python tests
	echo "test"

.PHONY: first_run
first_run: pull_mysql_docker docker_network create_database_docker python_docker python_docker_run ## Just run it all

.PHONY: docker_network
docker_network: ## Create a custom network to connect mysql command line client against mysql database docker
	@docker network create -d bridge $(NETWORK)

.PHONY: docker_remove_network
docker_remove_network: ## remove the custom network
	@docker network rm $(NETWORK)

.PHONY: python_docker
python_docker: ## Create docker to run this python project in
	@docker build -t $(PY_IMAGE_NAME) .

.PHONY: python_docker_run
python_docker_run: ## Run the python docker interactively
	@docker run -it --rm --network $(NETWORK) --name $(PY_CONTAINER_NAME) $(PY_IMAGE_NAME)

.PHONY: python_run_script
python_run_script:
	@docker run -it --rm --network $(NETWORK) --name $(PY_CONTAINER_NAME) $(PY_IMAGE_NAME) venv/bin/python3 main.py

.PHONY: pull_mysql_docker
pull_mysql_docker: ## Pull the mysql docker from docker hub
	@docker pull mysql

.PHONY: create_database_docker
create_database_docker: ## Spin up mysql docker and initialize database
	@docker run --name=$(DB_CONTAINER_NAME) \
	--network=$(NETWORK) \
	-e MYSQL_ROOT_PASSWORD=admin \
	-e MYSQL_DATABASE=$(DB_NAME) \
	-e MYSQL_USER=$(DB_USER) \
	-e MYSQL_PASSWORD=$(DB_PWD) \
	-p $(DB_CONTAINER_PORT):$(DB_CONTAINER_PORT) \
	-d mysql:latest

.PHONY: remove_database_docker
remove_database_docker: ## Stop the running container and remove it
	@docker stop $(DB_CONTAINER_NAME)
	@docker container rm $(DB_CONTAINER_NAME)

.PHONY: start_database_docker
start_database_docker: ## Start a stopped db container
	@docker start $(DB_CONTAINER_NAME)

.PHONY: clean
clean: remove_database_docker docker_remove_network
