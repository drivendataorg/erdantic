# erdantic

[![Docs Status](https://img.shields.io/badge/docs-latest-blueviolet)](https://nervous-visvesvaraya-4b7042.netlify.app/)
[![PyPI](https://img.shields.io/pypi/v/erdantic.svg)](https://pypi.org/project/erdantic/)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/erdantic.svg)](https://anaconda.org/conda-forge/erdantic)
[![tests](https://github.com/drivendataorg/erdantic/workflows/tests/badge.svg?branch=main)](https://github.com/drivendataorg/erdantic/actions?query=workflow%3Atests+branch%3Amain)
[![codecov](https://codecov.io/gh/drivendataorg/erdantic/branch/main/graph/badge.svg)](https://codecov.io/gh/drivendataorg/erdantic)


Draw [entity relationship diagrams (ERDs)](https://en.wikipedia.org/wiki/Data_modeling#Entity%E2%80%93relationship_diagrams) for Pydantic models and standard library dataclasses using the Graphviz library.

![](docs/docs/examples/pydantic.svg)

## Installation

Installing erdantic first requires [Graphviz](https://graphviz.org/), a venerable open-source graph visualization C library. You can install graphviz with [conda](https://anaconda.org/anaconda/graphviz) or with [other package managers](https://graphviz.org/download/).

To install erdantic:

```bash
pip install https://github.com/drivendataorg/cloudpathlib.git#egg=cloudpathlib[all]
```
