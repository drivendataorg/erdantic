import filecmp
import imghdr
import os
from pathlib import Path
import shutil

import pytest

import erdantic as erd
import erdantic._version
import erdantic.core
import erdantic.examples
from tests.utils import assert_dot_equals

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
OUTPUTS_DIR = Path(__file__).resolve().parent / "_outputs"


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


@pytest.fixture(scope="module", autouse=True)
def outputs_dir():
    shutil.rmtree(OUTPUTS_DIR, ignore_errors=True)
    OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)
    yield OUTPUTS_DIR


@pytest.mark.parametrize("case", CASES)
def test_draw_png_against_static_assets(case, version_patch):
    """Uses draw convenience function."""
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.png"

    out_path = OUTPUTS_DIR / f"{plugin}.png"

    erd.draw(model_or_module, out=out_path)
    assert imghdr.what(out_path) == "png"
    if not os.getenv("GITHUB_ACTIONS", False):
        # Skip for CI because it doesn't produce an identical file
        assert filecmp.cmp(out_path, expected_path), (out_path, expected_path)


@pytest.mark.parametrize("case", CASES)
def test_draw_svg_against_static_assets(case, version_patch):
    """Uses draw convenience function."""
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.svg"

    out_path = OUTPUTS_DIR / f"{plugin}.svg"
    erd.draw(model_or_module, out=out_path)
    assert out_path.read_text() == expected_path.read_text()


@pytest.mark.parametrize("case", CASES)
def test_to_dot_against_static_assets(case, version_patch):
    """Uses to_dot convenience function."""
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.dot"

    out_path = OUTPUTS_DIR / f"{plugin}.dot"
    out = erd.to_dot(model_or_module)
    out_path.write_text(out)
    assert_dot_equals(out, expected_path.read_text())


@pytest.mark.parametrize("case", CASES)
def test_json_against_static_assets(case, version_patch):
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.json"

    out_path = OUTPUTS_DIR / f"{plugin}.json"
    diagram = erd.create(model_or_module)
    out_json = diagram.model_dump_json(indent=2)
    out_path.write_text(out_json)
    assert out_json == expected_path.read_text()

    expected_diagram = erd.EntityRelationshipDiagram.model_validate_json(expected_path.read_text())
    assert diagram == expected_diagram
