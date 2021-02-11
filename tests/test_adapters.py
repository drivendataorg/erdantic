import filecmp
from pathlib import Path
import subprocess
import textwrap

import pytest
from pytest_cases import param_fixtures

import erdantic as erd
import erdantic.erd
import erdantic.examples.dataclasses
import erdantic.examples.pydantic
from erdantic.dataclasses import DataClassField, DataClassModel
from erdantic.pydantic import PydanticField, PydanticModel

from tests.utils import assert_dot_equals


ASSETS_DIR = Path(__file__).parent / "assets"

# key, model class, field class, examples module
adapter_sets = [
    ("dataclasses", DataClassModel, DataClassField, erdantic.examples.dataclasses),
    ("pydantic", PydanticModel, PydanticField, erdantic.examples.pydantic),
]
key, model_class, field_class, examples = param_fixtures(
    argnames="key, model_class, field_class, examples",
    argvalues=adapter_sets,
    ids=[a[0] for a in adapter_sets],
)


@pytest.fixture()
def version_patch(monkeypatch):
    """Monkeypatch version to stable value to compare with static test assets."""
    monkeypatch.setattr(erdantic.erd, "__version__", "TEST")


def test_is_model_type(model_class, examples):

    assert model_class.is_model_type(examples.Party)

    class JustAClass:
        attr: str

    assert not model_class.is_model_type(JustAClass)


def test_model_graph_search(examples):
    diagram = erd.create(examples.Party)
    assert {m.model for m in diagram.models} == {
        examples.Party,
        examples.Adventurer,
        examples.Quest,
        examples.QuestGiver,
    }
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {
        (examples.Party, examples.Adventurer),
        (examples.Party, examples.Quest),
        (examples.Quest, examples.QuestGiver),
    }


def test_model_name(model_class, examples):
    for model_name in ["Adventurer", "Party", "Quest", "QuestGiver"]:
        model = model_class(getattr(examples, model_name))
        assert model.name == model_name


def test_model_fields(model_class, examples):
    model = model_class(examples.Party)
    [f.name for f in model.fields] == ["name", "formed_datetime", "members", "active_quest"]
    [f.type_name for f in model.fields] == [
        "str",
        "datetime",
        "List[Adventurer]",
        "Optional[Quest]",
    ]


def test_model_comparisons(model_class, examples):
    assert model_class(examples.Party) == model_class(examples.Party)
    assert model_class(examples.Party) != model_class(examples.Adventurer)
    assert model_class(examples.Party) in [model_class(examples.Party)]
    assert model_class(examples.Party) in {model_class(examples.Party)}
    assert model_class(examples.Party) not in {model_class(examples.Adventurer)}


def test_field_comparisons(model_class, field_class, examples):
    raw_fields = [f.field for f in model_class(examples.Party).fields]
    assert field_class(raw_fields[0]) == field_class(raw_fields[0])
    assert field_class(raw_fields[0]) != field_class(raw_fields[1])
    assert field_class(raw_fields[0]) in [field_class(raw_fields[0])]
    assert field_class(raw_fields[0]) in {field_class(raw_fields[0])}
    assert field_class(raw_fields[0]) not in {field_class(raw_fields[1])}


def test_draw_png(key, examples, tmp_path, version_patch):
    # expected_path = ASSETS_DIR / key / "diagram.png"

    diagram = erd.create(examples.Party)
    path1 = tmp_path / "diagram1.png"
    diagram.draw(path1)
    assert path1.exists()

    path2 = tmp_path / "diagram2.png"
    erd.draw(examples.Party, out=path2)
    assert path2.exists()

    assert filecmp.cmp(path1, path2)
    # assert filecmp.cmp(path1, expected_path)


def test_draw_svg(key, examples, tmp_path, version_patch):
    # expected_path = ASSETS_DIR / key / "diagram.svg"

    diagram = erd.create(examples.Party)
    path1 = tmp_path / "diagram1.svg"
    diagram.draw(path1)
    assert path1.exists()

    path2 = tmp_path / "diagram2.svg"
    erd.draw(examples.Party, out=path2)
    assert path2.exists()

    assert filecmp.cmp(path1, path2)
    # assert filecmp.cmp(path1, expected_path)


def test_to_dot(key, examples, version_patch):
    expected_path = ASSETS_DIR / key / "diagram.dot"

    diagram = erd.create(examples.Party)
    dot = diagram.to_dot()
    assert dot == erd.to_dot(examples.Party)
    assert isinstance(dot, str)
    with expected_path.open("r") as fp:
        assert_dot_equals(dot, fp.read())


def test_registration(key):
    script = textwrap.dedent(
        f"""\
        from erdantic.base import model_adapter_registry;
        assert "{key}" in model_adapter_registry;
        """
    ).replace("\n", "")

    result = subprocess.run(
        ["python", "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert result.returncode == 0
