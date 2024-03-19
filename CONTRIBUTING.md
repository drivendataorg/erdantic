# Contributing to erdantic

...

## Local development

[![Nox](https://img.shields.io/badge/%F0%9F%A6%8A-Nox-D85E00.svg)](https://github.com/wntrblm/nox)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

This project is set up using [nox](https://nox.thea.codes/en/stable/) for automation. We recommend you install nox as a global tool with [pipx](https://pipx.pypa.io/):

```bash
pipx install nox
```

Many of the nox sessions are configured to use conda environments. erdantic depends on [graphviz](https://graphviz.org/), a C library, so conda is handy for installing it together alongside the Python dependencies. We recommend you install conda through the [miniforge](https://github.com/conda-forge/miniforge) distribution, which automatically comes with the faster mamba installer. 

### Development environment

To create a development environment, run: 

```bash 
nox -s dev
``` 

This will create a conda environment in `.nox/dev`. You can activate it with:

```bash
conda activate .nox/dev
```

### Tests

To run the full test matrix on all Python versions, run:

```bash
nox -s tests
```

To run tests for a specific version, use `tests-{python-version}`, e.g.,

```bash
nox -s tests-3.11
```

### Code quality

We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting, and we use [mypy](https://github.com/python/mypy) for type-checking. You can run them with the following nox sessions:

```bash
nox -s lint
nox -s typecheck
```
