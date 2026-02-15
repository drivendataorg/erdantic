python := "3.13"
python_nodot := replace(python, ".", "")

# Print this help documentation
help:
    just --list

# Sync requirements
sync:
    pixi run true

# Run linting
lint:
    pixi run ruff format --check
    pixi run ruff check

# Run formatting
format:
    pixi run ruff format
    pixi run ruff check --fix

# Run static typechecking
typecheck:
    pixi run -e typecheck \
        mypy erdantic --install-types --non-interactive

# Run the tests
test *args:
    pixi run -e test-py{{python_nodot}} python -I -m pytest {{args}}

# Run all tests with Python version matrix
test-all *args:
    for python in 3.9 3.10 3.11 3.12 3.13; do \
        just python=$python test {{args}}; \
    done

# Generate static test and documentation assets
generate-static-assets: generate-static-docs-assets generate-static-test-assets

[private]
generate-static-docs-assets:
    pixi run python docs/generate_images.py
    pixi run python docs/generate_pydantic_with_default_column_diagram.py

[private]
generate-static-test-assets:
    pixi run -e test-py313 python tests/scripts/generate_static_assets.py py_lt_314
    pixi run -e test-py313 python tests/scripts/generate_pydantic_with_defaults_assets.py py_lt_314
    pixi run -e test-py314 python tests/scripts/generate_static_assets.py py_gte_314
    pixi run -e test-py314 python tests/scripts/generate_pydantic_with_defaults_assets.py py_gte_314

# Run example documents
run-notebooks:
    mkdir -p docs/docs/examples
    for notebook in docs/notebooks/examples/*.ipynb; do \
        pixi run jupyter execute --output ../../docs/examples/$(basename $notebook) $notebook; \
    done
    mkdir -p docs/docs/output-formats
    for notebook in docs/notebooks/output-formats/*.ipynb; do \
        pixi run jupyter execute --output ../../docs/output-formats/$(basename $notebook) $notebook; \
    done

# Generate docs
docs: run-notebooks
    (cd docs && pixi run mkdocs build)

# Serve docs
docs-serve: run-notebooks
    (cd docs && pixi run mkdocs serve)
