import filecmp
import imghdr
from pathlib import Path

import pytest

import erdantic as erd
import erdantic._version
import erdantic.core
import erdantic.examples
from tests.utils import assert_dot_equals

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


@pytest.fixture()
def version_patch(monkeypatch):
    """Monkeypatch version to stable value to compare with static test assets."""
    default_graph_attrs = dict(erdantic.core._DEFAULT_GRAPH_ATTRS)
    default_graph_attrs["label"] = default_graph_attrs["label"].replace(
        f"v{erdantic.__version__}", "vTEST"
    )
    monkeypatch.setattr(erdantic.core, "_DEFAULT_GRAPH_ATTRS", tuple(default_graph_attrs.items()))

    monkeypatch.setattr(erd, "__version__", "TEST")
    monkeypatch.setattr(erdantic._version, "__version__", "TEST")
    monkeypatch.setattr(erdantic.core, "__version__", "TEST")


CASES = (
    ("attrs", erdantic.examples.attrs),
    ("dataclasses", erdantic.examples.dataclasses),
    ("pydantic", erdantic.examples.pydantic),
    ("pydantic_v1", erdantic.examples.pydantic_v1),
    ("attrs", erdantic.examples.attrs.Party),
    ("dataclasses", erdantic.examples.dataclasses.Party),
    ("pydantic", erdantic.examples.pydantic.Party),
    ("pydantic_v1", erdantic.examples.pydantic_v1.Party),
)


@pytest.mark.parametrize("case", CASES)
def test_draw_png_against_static_assets(case, tmp_path, version_patch):
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / plugin / "diagram.png"

    out_path = tmp_path / "diagram.png"
    erd.draw(model_or_module, out=out_path)
    assert imghdr.what(out_path) == "png"
    assert filecmp.cmp(out_path, expected_path)


@pytest.mark.parametrize("case", CASES)
def test_draw_svg_against_static_assets(case, tmp_path, version_patch):
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / plugin / "diagram.svg"

    out_path = tmp_path / "diagram.svg"
    erd.draw(model_or_module, out=out_path)
    assert filecmp.cmp(out_path, expected_path), (out_path, expected_path)


@pytest.mark.parametrize("case", CASES)
def test_to_dot_against_static_assets(case, tmp_path, version_patch):
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / plugin / "diagram.dot"

    out = erd.to_dot(model_or_module)
    assert_dot_equals(out, expected_path.read_text())


@pytest.mark.parametrize("case", CASES)
def test_json_against_static_assets(case, tmp_path, version_patch):
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / plugin / "diagram.json"

    diagram = erd.create(model_or_module)
    assert diagram.model_dump_json(indent=2) == expected_path.read_text()

    expected_diagram = erd.EntityRelationshipDiagram.model_validate_json(expected_path.read_text())
    assert diagram == expected_diagram
