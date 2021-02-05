# erdantic: Entity Relationship Diagrams

[![Docs Status](https://img.shields.io/badge/docs-latest-blueviolet)](https://nervous-visvesvaraya-4b7042.netlify.app/)
[![PyPI](https://img.shields.io/pypi/v/erdantic.svg)](https://pypi.org/project/erdantic/)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/erdantic.svg)](https://anaconda.org/conda-forge/erdantic)
[![tests](https://github.com/drivendataorg/erdantic/workflows/tests/badge.svg?branch=main)](https://github.com/drivendataorg/erdantic/actions?query=workflow%3Atests+branch%3Amain)
[![codecov](https://codecov.io/gh/drivendataorg/erdantic/branch/main/graph/badge.svg)](https://codecov.io/gh/drivendataorg/erdantic)

**erdantic** is a simple tool for drawing [entity relationship diagrams (ERDs)](https://en.wikipedia.org/wiki/Data_modeling#Entity%E2%80%93relationship_diagrams) for Python data model classes. Diagrams are rendered using the venerable Graphviz library. Supported data modeling frameworks are:

- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html) from the Python standard library

Features include a CLI, native rendering in Jupyter notebook, and an architecture easily extensible to other data modeling frameworks.

![Example diagram created by erdantic](docs/docs/examples/pydantic.svg)

## Installation

Installing erdantic first requires [Graphviz](https://graphviz.org/), an open-source graph visualization C library. You can install Graphviz with [conda](https://anaconda.org/anaconda/graphviz) or with [other package managers](https://graphviz.org/download/).

To install erdantic:

```bash
pip install https://github.com/drivendataorg/erdantic.git#egg=erdantic
```

## Quick Usage

The fastest way to produce a diagram like the above example is to use the provided CLI. Simply pass a full dotted path to your data model class and an output path.

```bash
erdantic erdantic.examples.pydantic.Party -o diagram.png
```

You can also use the Python library.

```bash
import erdantic as erd
from erdantic.examples.pydantic import Party

# Easy one-liner
erd.draw(Party, path="diagram.png")

# Or create a diagram object that you can inspect and do stuff with
diagram = erd.create_erd(Party)
diagram.draw("diagram.png")
```
