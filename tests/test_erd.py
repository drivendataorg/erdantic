import imghdr

import pytest

import erdantic as erd
from erdantic.erd import Edge
from erdantic.errors import UnknownModelTypeError
from erdantic.examples.pydantic import Party, Quest


def test_diagram_comparisons():
    diagram1 = erd.create(Party)
    diagram2 = erd.create(Party)
    diagram3 = erd.create(Quest)
    assert diagram1 == diagram2
    assert diagram1 != diagram3
    assert diagram1 in [diagram2]
    assert diagram1 in {diagram2}
    assert diagram1 not in [diagram3]


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


def test_not_a_type_error():
    with pytest.raises(ValueError, match="Given model is not a type"):
        erd.create(5)


def test_unknown_model_type_error():
    class BadModel:
        pass

    with pytest.raises(UnknownModelTypeError) as e_info:
        erd.create(BadModel)

    e = e_info.value
    assert e.model is BadModel
    assert "Given model does not match any supported types" in str(e)
    assert BadModel.__name__ in str(e)


def test_draw(tmp_path):
    path = tmp_path / "diagram.png"
    erd.draw(Party, out=path)
    assert imghdr.what(path) == "png"


def test_repr():
    diagram = erd.create(Party)
    assert repr(diagram) and isinstance(repr(diagram), str)
    assert repr(diagram.edges[0]) and isinstance(repr(diagram.edges[0]), str)


def test_repr_png():
    diagram = erd.create(Party)
    png = diagram._repr_png_()
    assert png and isinstance(png, bytes)
    assert imghdr.what("", h=png) == "png"


def test_repr_svg():
    diagram = erd.create(Party)
    svg = diagram._repr_svg_()
    assert svg and isinstance(svg, str)
