import pytest

import erdantic as erd
from erdantic.examples.pydantic import Party
from erdantic.erd import Edge, Field, Model


def test_abstract_field_instatiation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Field()


def test_abstract_model_instation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Model()


def test_edge_comparisons():
    diagram = erd.create(Party)
    edges = diagram.edges
    edge0_copy = Edge(
        source=edges[0].source, source_field=edges[0].source_field, target=edges[0].target
    )
    assert edges[0] == edge0_copy
    assert edges[1] != edge0_copy
    assert edges[0] in [edge0_copy]
    assert edges[0] in {edge0_copy}
    assert edges[0] not in {edges[1]}


def test_repr():
    diagram = erd.create(Party)
    assert repr(diagram) and isinstance(repr(diagram), str)
    assert repr(diagram.models[0]) and isinstance(repr(diagram.models[0]), str)
    assert repr(diagram.models[0].fields[0]) and isinstance(repr(diagram.models[0].fields[0]), str)
    assert repr(diagram.edges[0]) and isinstance(repr(diagram.edges[0]), str)
