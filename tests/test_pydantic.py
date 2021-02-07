import filecmp

from pydantic import BaseModel

import erdantic as erd
from erdantic.pydantic import PydanticDiagramFactory, PydanticField, PydanticModel
from erdantic.examples.pydantic import Adventurer, Party, Quest, QuestGiver


def test_is_type():
    factory = PydanticDiagramFactory()

    class IsAPydanticModel(BaseModel):
        attr: str

    assert factory.is_type(IsAPydanticModel)

    class NotAPydanticModel:
        attr: str

    assert not factory.is_type(NotAPydanticModel)


def test_create_diagram():
    factory = PydanticDiagramFactory()
    diagram = factory.create(Party)
    assert isinstance(diagram, erd.EntityRelationshipDiagram)
    assert diagram == erd.create(Party)


def test_model_graph_search():
    diagram = erd.create(Party)
    assert {m.pydantic_model for m in diagram.models} == {Party, Adventurer, Quest, QuestGiver}
    assert {(e.source.pydantic_model, e.target.pydantic_model) for e in diagram.edges} == {
        (Party, Adventurer),
        (Party, Quest),
        (Quest, QuestGiver),
    }


def test_model_comparisons():
    assert PydanticModel(Party) == PydanticModel(Party)
    assert PydanticModel(Party) != PydanticModel(Adventurer)
    assert PydanticModel(Party) in [PydanticModel(Party)]
    assert PydanticModel(Party) in {PydanticModel(Party)}
    assert PydanticModel(Party) not in {PydanticModel(Adventurer)}


def test_field_comparisons():
    fields = list(Party.__fields__.values())
    assert PydanticField(fields[0]) == PydanticField(fields[0])
    assert PydanticField(fields[0]) != PydanticField(fields[1])
    assert PydanticField(fields[0]) in [PydanticField(fields[0])]
    assert PydanticField(fields[0]) in {PydanticField(fields[0])}
    assert PydanticField(fields[0]) not in {PydanticField(fields[1])}


def test_draw(tmp_path):
    diagram = erd.create(Party)
    path1 = tmp_path / "diagram1.png"
    diagram.draw(path1)
    assert path1.exists()

    path2 = tmp_path / "diagram2.png"
    erd.draw(Party, out=path2)
    assert path2.exists()

    assert filecmp.cmp(path1, path2)


def test_to_dot():
    diagram = erd.create(Party)
    dot = diagram.to_dot()
    assert dot == erd.to_dot(Party)
    assert isinstance(dot, str)
    assert dot
