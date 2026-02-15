import filecmp
import os
from pathlib import Path
import sys

import filetype
import pytest

import erdantic as erd
import erdantic._version
import erdantic.core
import erdantic.examples
from tests.snapshot_cases import SNAPSHOT_CASES as SNAPSHOT_MODEL_CASES
from tests.utils import assert_dot_equals

if sys.version_info < (3, 14):
    ASSETS_SUBDIR = "py_lt_314"
else:
    ASSETS_SUBDIR = "py_gte_314"

ASSETS_DIR = Path(__file__).resolve().parent / "assets" / ASSETS_SUBDIR

EXAMPLE_CASES = [
    ("attrs", erdantic.examples.attrs),
    ("dataclasses", erdantic.examples.dataclasses),
    ("pydantic", erdantic.examples.pydantic),
    ("attrs", erdantic.examples.attrs.Party),
    ("dataclasses", erdantic.examples.dataclasses.Party),
    ("pydantic", erdantic.examples.pydantic.Party),
]

if sys.version_info < (3, 14):
    EXAMPLE_CASES.extend(
        [
            ("pydantic_v1", erdantic.examples.pydantic_v1),
            ("pydantic_v1", erdantic.examples.pydantic_v1.Party),
        ]
    )


SNAPSHOTS_DIR = ASSETS_DIR / "snapshots"


@pytest.mark.parametrize("case", EXAMPLE_CASES)
def test_draw_png_examples_against_static_assets(case, outputs_dir, version_patch):
    """Uses draw convenience function for user-facing examples."""
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.png"
    out_path = outputs_dir / f"{plugin}.png"

    erd.draw(model_or_module, out=out_path)
    kind = filetype.guess(out_path)
    assert kind is not None
    assert kind.mime == "image/png"
    if not os.getenv("GITHUB_ACTIONS", False):
        # Skip for CI because it doesn't produce an identical file
        assert filecmp.cmp(out_path, expected_path), (out_path, expected_path)


@pytest.mark.parametrize("case", EXAMPLE_CASES)
def test_draw_svg_examples_against_static_assets(case, outputs_dir, version_patch):
    """Uses draw convenience function for user-facing examples."""
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.svg"
    out_path = outputs_dir / f"{plugin}.svg"

    erd.draw(model_or_module, out=out_path)
    if not os.getenv("GITHUB_ACTIONS", False):
        # Skip for CI because it doesn't produce an identical file
        assert out_path.read_text() == expected_path.read_text()


@pytest.mark.parametrize("case", EXAMPLE_CASES)
def test_to_dot_examples_against_static_assets(case, outputs_dir, version_patch):
    """Uses to_dot convenience function for user-facing examples."""
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.dot"
    out_path = outputs_dir / f"{plugin}.dot"

    out = erd.to_dot(model_or_module)
    out_path.write_text(out)
    assert_dot_equals(out, expected_path.read_text())


@pytest.mark.parametrize("case", EXAMPLE_CASES)
def test_json_examples_against_static_assets(case, outputs_dir, version_patch):
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.json"
    out_path = outputs_dir / f"{plugin}.json"

    diagram = erd.create(model_or_module)
    out_json = diagram.model_dump_json(indent=2)
    out_path.write_text(out_json)
    assert out_json == expected_path.read_text()

    expected_diagram = erd.EntityRelationshipDiagram.model_validate_json(expected_path.read_text())
    assert diagram == expected_diagram


@pytest.mark.parametrize("case", EXAMPLE_CASES)
def test_to_d2_examples_against_static_assets(case, outputs_dir, version_patch):
    """Uses to_d2 method to test against static assets for user-facing examples."""
    plugin, model_or_module = case
    expected_path = ASSETS_DIR / f"{plugin}.d2"
    diagram = erd.create(model_or_module)
    out = diagram.to_d2()
    out_path = outputs_dir / f"{plugin}.d2"
    out_path.write_text(out)
    assert out.strip() == expected_path.read_text().strip()


@pytest.mark.parametrize("case", SNAPSHOT_MODEL_CASES)
def test_to_dot_snapshots_against_static_assets(case, outputs_dir, version_patch):
    """Uses to_dot convenience function for test-focused snapshots."""
    case_name, model = case
    expected_path = SNAPSHOTS_DIR / f"{case_name}.dot"
    out_dir = outputs_dir / "snapshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{case_name}.dot"
    out = erd.to_dot(model)
    out_path.write_text(out)
    assert_dot_equals(out, expected_path.read_text())


@pytest.mark.parametrize("case", SNAPSHOT_MODEL_CASES)
def test_to_d2_snapshots_against_static_assets(case, outputs_dir, version_patch):
    """Uses to_d2 method for test-focused snapshots."""
    case_name, model = case
    expected_path = SNAPSHOTS_DIR / f"{case_name}.d2"
    out_dir = outputs_dir / "snapshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{case_name}.d2"
    diagram = erd.create(model)
    out = diagram.to_d2()
    out_path.write_text(out)
    assert out.strip() == expected_path.read_text().strip()
