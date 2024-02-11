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
	rm -f coverage.xml
	rm -fr htmlcov/
	rm -fr .pytest_cache

dist: clean ## builds source and wheel package
	python -m build
	ls -l dist

docs: clean-docs ## build documentation
	echo "# CLI Help Documentation\n" > docs/docs/cli.md
	@echo '```bash' >> docs/docs/cli.md
	@echo "erdantic --help" >> docs/docs/cli.md
	@echo '```' >> docs/docs/cli.md
	@echo "" >> docs/docs/cli.md
	@echo '```' >> docs/docs/cli.md
	@erdantic --help >> docs/docs/cli.md
	@echo '```' >> docs/docs/cli.md
	sed 's|https://raw.githubusercontent.com/drivendataorg/erdantic/main/docs/docs/examples/pydantic.svg|examples/pydantic.svg|g' README.md \
		| sed 's|https://erdantic.drivendata.org/stable/||g' \
		> docs/docs/index.md
	sed 's|https://erdantic.drivendata.org/stable/||g' HISTORY.md > docs/docs/changelog.md
	rm -f docs/docs/examples/diagram.png
	cd docs && mkdocs build

docs-notebooks:
	rm -f docs/docs/examples/diagram.png
	jupyter nbconvert --execute --clear-output docs/docs/examples/pydantic.ipynb
	rm -f docs/docs/examples/diagram.png
	jupyter nbconvert --execute --clear-output docs/docs/examples/dataclasses.ipynb
	rm -f docs/docs/examples/diagram.png

format: ## format code with black
	ruff format erdantic tests docs
	ruff check --fix erdantic tests docs

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

lint: ## run linting and code quality checks
	ruff format --check erdantic tests docs
	ruff check erdantic tests docs

pypitest: dist
	twine upload --repository testpypi dist/*

requirements: ## install development requirements
	pip install -r requirements-dev.txt

static-test-assets:
	python tests/scripts/generate_static_assets.py

test: ## run tests
	python -m pytest -vv

typecheck: ## run mypy typechecking
	mypy --install-types --non-interactive erdantic
