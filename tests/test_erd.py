import filecmp
import imghdr

import pytest

import erdantic as erd
from erdantic.erd import Edge, find_models
from erdantic.exceptions import (
    NotATypeError,
    InvalidModelAdapterError,
    ModelAdapterNotFound,
    UnknownModelTypeError,
)
from erdantic.examples.pydantic import Party, Quest
import erdantic.examples.pydantic as examples_pydantic
import erdantic.examples.dataclasses as examples_dataclasses
from erdantic.pydantic import PydanticModel


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

    # Bad comparison should raise error
    with pytest.raises(TypeError, match="not supported"):
        edges[0] < str(edges[0])


def test_not_a_type_error():
    with pytest.raises(NotATypeError, match="Given model is not a type"):
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


def test_draw_with_terminus(tmp_path):
    # use EntityRelationshipDiagram.draw as expected
    expected_path = tmp_path / "expected.png"
    diagram = erd.create(Party, termini=[Quest])
    diagram.draw(expected_path)

    path = tmp_path / "diagram.png"
    erd.draw(Party, out=path, termini=[Quest])
    assert imghdr.what(path) == "png"
    assert filecmp.cmp(path, expected_path)


def test_to_dot_with_terminus(tmp_path):
    # use EntityRelationshipDiagram.to_dot as expected
    diagram = erd.create(Party, termini=[Quest])
    assert erd.to_dot(Party, termini=[Quest]) == diagram.to_dot()


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


def test_find_models():
    expected_pydantic_models = {
        examples_pydantic.Party,
        examples_pydantic.Adventurer,
        examples_pydantic.Quest,
        examples_pydantic.QuestGiver,
    }
    assert set(find_models(examples_pydantic)) == expected_pydantic_models
    assert (
        set(find_models(examples_pydantic, model_adapters=["pydantic"]))
        == expected_pydantic_models
    )
    assert (
        set(find_models(examples_pydantic, model_adapters=[PydanticModel]))
        == expected_pydantic_models
    )
    assert set(find_models(examples_pydantic, model_adapters=["dataclasses"])) == set()

    with pytest.raises(ModelAdapterNotFound):
        list(find_models(examples_pydantic, model_adapters=["unknown_key"]))

    with pytest.raises(InvalidModelAdapterError):
        list(find_models(examples_pydantic, model_adapters=[examples_pydantic.Party]))

    expected_dataclasses_models = {
        examples_dataclasses.Party,
        examples_dataclasses.Adventurer,
        examples_dataclasses.Quest,
        examples_dataclasses.QuestGiver,
    }
    assert set(find_models(examples_dataclasses)) == expected_dataclasses_models
