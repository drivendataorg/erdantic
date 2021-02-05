.PHONY: clean clean-docs clean-pyc clean-test clean-build docs format lint release release-test test help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

docs: clean-docs ## build documentation
	sed 's|docs/docs/examples/pydantic.svg|examples/pydantic.svg|g' README.md > docs/docs/index.md
	cd docs && mkdocs build

format: ## format code with black
	black erdantic tests docs

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

lint: ## run linting and code quality checks
	black --check erdantic tests docs
	flake8 erdantic tests docs

requirements: ## install development requirements
	pip install -r requirements-dev.txt

test: ## run tests
	python -m pytest -v

typecheck: ## run mypy typechecking
	mypy erdantic
