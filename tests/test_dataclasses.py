import dataclasses
import filecmp

import erdantic as erd
from erdantic.dataclasses import DataClassModel, DataClassField
from erdantic.examples.dataclasses import Adventurer, Party, Quest, QuestGiver


def test_model_graph_search():
    diagram = erd.create(Party)
    assert {m.dataclass for m in diagram.models} == {Party, Adventurer, Quest, QuestGiver}
    assert {(e.source.dataclass, e.target.dataclass) for e in diagram.edges} == {
        (Party, Adventurer),
        (Party, Quest),
        (Quest, QuestGiver),
    }


def test_model_comparisons():
    assert DataClassModel(Party) == DataClassModel(Party)
    assert DataClassModel(Party) != DataClassModel(Adventurer)
    assert DataClassModel(Party) in [DataClassModel(Party)]
    assert DataClassModel(Party) in {DataClassModel(Party)}
    assert DataClassModel(Party) not in {DataClassModel(Adventurer)}


def test_field_comparisons():
    fields = list(dataclasses.fields(Party))
    assert DataClassField(fields[0]) == DataClassField(fields[0])
    assert DataClassField(fields[0]) != DataClassField(fields[1])
    assert DataClassField(fields[0]) in [DataClassField(fields[0])]
    assert DataClassField(fields[0]) in {DataClassField(fields[0])}
    assert DataClassField(fields[0]) not in {DataClassField(fields[1])}


def test_draw(tmp_path):
    diagram = erd.create(Party)
    path1 = tmp_path / "diagram1.png"
    diagram.draw(path1)
    assert path1.exists()

    path2 = tmp_path / "diagram2.png"
    erd.draw(Party, path=path2)
    assert path2.exists()

    assert filecmp.cmp(path1, path2)


def test_to_dot():
    diagram = erd.create(Party)
    dot = diagram.to_dot()
    assert dot == erd.to_dot(Party)
    assert isinstance(dot, str)
    assert dot
