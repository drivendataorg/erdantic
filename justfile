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
test-all:
    for python in 3.9 3.10 3.11 3.12 3.13; do \
        just python=$python test; \
    done

# https://github.com/conda-forge/graphviz-feedstock/issues/152
# Fix graphviz plugin registration. Needed for osx-arm64
fix-graphviz:
    just fix-graphviz-default
    for python in 3.9 3.10 3.11 3.12 3.13; do \
        just python=$python fix-graphviz-test; \
    done

[private]
fix-graphviz-default:
    compgen -G .pixi/envs/default/lib/graphviz/config* > /dev/null \
            || pixi run -e default dot -c \
            || true

[private]
fix-graphviz-test:
    compgen -G .pixi/envs/test-py{{python_nodot}}/lib/graphviz/config* > /dev/null \
        || pixi run -e test-py{{python_nodot}} dot -c \
        || true

# Generate static test and documentation assets
generate-static-assets: generate-static-docs-assets generate-static-test-assets

[private]
generate-static-docs-assets:
    pixi run python docs/generate_images.py
    pixi run python docs/generate_pydantic_with_default_column_diagram.py

[private]
generate-static-test-assets:
    pixi run python tests/scripts/generate_static_assets.py
    pixi run python tests/scripts/generate_pydantic_with_defaults_assets.py

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
