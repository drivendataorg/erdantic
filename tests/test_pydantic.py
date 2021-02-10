import filecmp
import subprocess
import textwrap
from typing import Dict, Tuple

from pydantic import BaseModel

import erdantic as erd
from erdantic.pydantic import PydanticField, PydanticModel
from erdantic.examples.pydantic import Adventurer, Party, Quest, QuestGiver


def test_is_model_type():
    class IsAPydanticModel(BaseModel):
        attr: str

    assert PydanticModel.is_model_type(IsAPydanticModel)

    class NotAPydanticModel:
        attr: str

    assert not PydanticModel.is_model_type(NotAPydanticModel)


def test_model_graph_search():
    diagram = erd.create(Party)
    assert {m.model for m in diagram.models} == {Party, Adventurer, Quest, QuestGiver}
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {
        (Party, Adventurer),
        (Party, Quest),
        (Quest, QuestGiver),
    }


def test_model_graph_search_nested_args():
    class Inner0(BaseModel):
        id: int

    class Inner1(BaseModel):
        id: int

    class Outer(BaseModel):
        inner: Dict[str, Tuple[Inner0, Inner1]]

    diagram = erd.create(Outer)
    assert {m.model for m in diagram.models} == {Outer, Inner0, Inner1}
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {
        (Outer, Inner0),
        (Outer, Inner1),
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


def test_registration():
    script = textwrap.dedent(
        """\
        from erdantic.base import model_adapter_registry;
        assert "pydantic" in model_adapter_registry;
        """
    ).replace("\n", "")

    result = subprocess.run(
        ["python", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert result.returncode == 0
