# Contributing to erdantic

## Report a bug or request a feature

Please file an issue in the [issue tracker](https://github.com/drivendataorg/erdantic/issues).

## External contributions

Pull requests from external contributors are welcome. However, we ask that any nontrivial changes be discussed with maintainers in an [issue](https://github.com/drivendataorg/erdantic/issues) first before submitting a pull request.

## Local development

[![Pixi Badge][https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json&style=flat-square
]][[pixi-url](https://pixi.sh)]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

This project is set up using [Pixi](https://pixi.sh) for managing environments and [Just](https://github.com/casey/just) as a task runner.

Many useful recipes are defined in the [`justfile`](./justfile). You can run:

```bash
just
```

to see available recipes with brief documentation.

### Development environment

Pixi handles the creation and synchronization of the default development environment. You can run commands in the environment like so:

```bash
pixi run {some shell command}
```

You can activate the default environment with

```bash
pixi shell
```

### Tests

```bash
just test
```

You can run the tests for a specific Python version with, for example:

```bash
just python=3.12 test
```

To run tests on all supported Python versions, run:

```bash
just test-all
```

### Code quality

We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting, and we use [mypy](https://github.com/python/mypy) for static type checking. You can run them with the following commands:

```bash
just lint
just typecheck
```
