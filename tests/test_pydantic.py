import filecmp

from erdantic import create_erd, draw, to_dot
from erdantic.pydantic import PydanticField, PydanticModel
from erdantic.examples.pydantic import Adventurer, Party, Quest, QuestGiver


def test_model_graph_search():
    diagram = create_erd(Party)
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
    diagram = create_erd(Party)
    path1 = tmp_path / "diagram1.png"
    diagram.draw(path1)
    assert path1.exists()

    path2 = tmp_path / "diagram2.png"
    draw(Party, path=path2)
    assert path2.exists()

    assert filecmp.cmp(path1, path2)


def test_to_dot():
    diagram = create_erd(Party)
    dot = diagram.to_dot()
    assert dot == to_dot(Party)
    assert isinstance(dot, str)
    assert dot
