# erdantic: Entity Relationship Diagrams

[![Docs Status](https://img.shields.io/badge/docs-stable-informational)](https://erdantic.drivendata.org/)
[![PyPI](https://img.shields.io/pypi/v/erdantic.svg)](https://pypi.org/project/erdantic/)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/erdantic.svg)](https://anaconda.org/conda-forge/erdantic)
[![conda-forge feedstock](https://img.shields.io/badge/conda--forge-feedstock-yellowgreen)](https://github.com/conda-forge/erdantic-feedstock)
[![tests](https://github.com/drivendataorg/erdantic/workflows/tests/badge.svg?branch=main)](https://github.com/drivendataorg/erdantic/actions?query=workflow%3Atests+branch%3Amain)
[![codecov](https://codecov.io/gh/drivendataorg/erdantic/branch/main/graph/badge.svg)](https://codecov.io/gh/drivendataorg/erdantic)

**erdantic** is a simple tool for drawing [entity relationship diagrams (ERDs)](https://en.wikipedia.org/wiki/Data_modeling#Entity%E2%80%93relationship_diagrams) for Python data model classes. Diagrams are rendered using the venerable [Graphviz](https://graphviz.org/) library. Supported data modeling frameworks are:

- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [Pydantic V1 legacy](https://docs.pydantic.dev/latest/migration/#continue-using-pydantic-v1-features)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html) from the Python standard library

Features include a convenient CLI, automatic native rendering in Jupyter notebooks, and easy extensibility to other data modeling frameworks. Docstrings are even accessible as tooltips for SVG outputs. Great for adding a simple and clean data model reference to your documentation.

<object type="image/svg+xml" data="https://raw.githubusercontent.com/drivendataorg/erdantic/main/docs/docs/examples/pydantic.svg" width="100%" typemustmatch><img alt="Example diagram created by erdantic" src="https://raw.githubusercontent.com/drivendataorg/erdantic/main/docs/docs/examples/pydantic.svg"></object>

## Installation

erdantic's graph modeling depends on [pygraphviz](https://pygraphviz.github.io/documentation/stable/index.html) and [Graphviz](https://graphviz.org/), an open-source C library. If you are on Linux or macOS, the easiest way to install everything together is to use conda and conda-forge:

```bash
conda install erdantic -c conda-forge
```

If not using conda, Graphviz must be installed first (before you can install pygraphviz). For recommended options and installation troubleshooting, see the [pygraphviz docs](https://pygraphviz.github.io/documentation/stable/install.html). Then to install erdantic and its Python dependencies from PyPI:

```bash
pip install erdantic
```

### Development version

You can get the development version from GitHub with:

```bash
pip install git+https://github.com/drivendataorg/erdantic.git#egg=erdantic
```

## Quick Usage

The fastest way to produce a diagram like the above example is to use the erdantic CLI. Simply specify the full dotted path to your data model class and an output path. The rendered format is interpreted from the filename extension.

```bash
erdantic erdantic.examples.pydantic.Party -o diagram.png
```

You can also import the erdantic Python library and use its functions.

```python
import erdantic as erd
from erdantic.examples.pydantic import Party

# Easy one-liner
erd.draw(Party, out="diagram.png")

# Or create a diagram object that you can inspect and do stuff with
diagram = erd.create(Party)
diagram.models
#> [PydanticModel(Adventurer), PydanticModel(Party), PydanticModel(Quest), PydanticModel(QuestGiver)]
diagram.draw("diagram.png")
```

Check out the "Usage Examples" section of our [docs](https://erdantic.drivendata.org/) to see more.
