import filecmp
import subprocess

import pytest
from typer.testing import CliRunner

import erdantic as erd
from erdantic._version import __version__
from erdantic.cli import app, import_object_from_name
import erdantic.examples.dataclasses as examples_dataclasses
import erdantic.examples.pydantic as examples_pydantic
from erdantic.examples.pydantic import Party, Quest
from erdantic.exceptions import ModelOrModuleNotFoundError

runner = CliRunner(mix_stderr=False)


def test_import_object_from_name():
    assert import_object_from_name("erdantic.examples.pydantic.Party") is Party
    assert import_object_from_name("erdantic.examples.pydantic.Quest") is Quest
    assert import_object_from_name("erdantic") is erd
    assert import_object_from_name("erdantic.examples.pydantic") is examples_pydantic
    with pytest.raises(ModelOrModuleNotFoundError):
        import_object_from_name("not_a_module")
    with pytest.raises(ModelOrModuleNotFoundError):
        import_object_from_name("erdantic.not_a_module")
    with pytest.raises(ModelOrModuleNotFoundError):
        import_object_from_name("erdantic.examples.pydantic.not_a_model_class")


def test_draw(outputs_dir):
    out_dir = outputs_dir / "test_cli-test_draw"
    out_dir.mkdir()

    # With library for comparison
    path_base = out_dir / "diagram_base.png"
    erd.draw(Party, out=path_base)
    assert path_base.exists()

    # With CLI
    path1 = out_dir / "diagram1.png"
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party", "-o", str(path1)])
    print(result.output)
    assert result.exit_code == 0
    assert path1.exists()
    assert filecmp.cmp(path1, path_base)

    # python -m erdantic
    path2 = out_dir / "diagram2.png"
    result = subprocess.run(
        ["python", "-m", "erdantic", "erdantic.examples.pydantic.Party", "-o", str(path2)],
        capture_output=True,
        universal_newlines=True,
    )
    print(result.stderr)
    print(result.stdout)
    assert result.returncode == 0
    assert path2.exists()
    assert filecmp.cmp(path2, path_base)


def test_with_terminal_model(outputs_dir):
    out_dir = outputs_dir / "test_cli-test_with_terminal_model"
    out_dir.mkdir()

    # With library for comparison
    path_base = out_dir / "diagram_base.png"
    erd.draw(Party, out=path_base, terminal_models=[Quest])
    assert path_base.exists()

    # With CLI
    path1 = out_dir / "diagram1.png"
    result = runner.invoke(
        app,
        [
            "erdantic.examples.pydantic.Party",
            "-t",
            "erdantic.examples.pydantic.Quest",
            "-o",
            str(path1),
        ],
    )
    print(result.output)
    assert result.exit_code == 0
    assert path1.exists()
    assert filecmp.cmp(path1, path_base)


def test_with_modules(outputs_dir):
    out_dir = outputs_dir / "test_cli-test_with_modules"
    out_dir.mkdir()

    # With library for comparison
    path_base = out_dir / "diagram_base.png"
    erd.draw(Quest, examples_dataclasses, out=path_base)
    assert path_base.exists()

    # With CLI
    path1 = out_dir / "diagram1.png"
    result = runner.invoke(
        app,
        [
            "erdantic.examples.pydantic.Quest",
            "erdantic.examples.dataclasses",
            "-o",
            str(path1),
        ],
    )
    print(result.output)
    assert result.exit_code == 0
    assert path1.exists()
    assert filecmp.cmp(path1, path_base)

    # With library for comparison, all pydantic classes
    path_base_all_pydantic = out_dir / "diagram_base_all_pydantic.png"
    erd.draw(Quest, examples_dataclasses, examples_pydantic, out=path_base_all_pydantic)
    assert path_base_all_pydantic.exists()

    # With CLI without limit_search_models_to
    path2 = out_dir / "diagram2.png"
    result = runner.invoke(
        app,
        [
            "erdantic.examples.pydantic.Quest",
            "erdantic.examples.dataclasses",
            "erdantic.examples.pydantic",
            "-o",
            str(path2),
        ],
    )
    print(result.output)
    assert result.exit_code == 0
    assert path2.exists()
    assert filecmp.cmp(path2, path_base_all_pydantic)

    # With CLI with limit_search_models_to
    path3 = out_dir / "diagram3.png"
    result = runner.invoke(
        app,
        [
            "erdantic.examples.pydantic.Quest",
            "erdantic.examples.dataclasses",
            "erdantic.examples.pydantic",
            "-o",
            str(path3),
            "-m",
            "dataclasses",
        ],
    )
    print(result.output)
    assert result.exit_code == 0
    assert path3.exists()
    assert filecmp.cmp(path3, path_base)


def test_missing_out():
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party"])
    print(result.output)
    assert result.exit_code == 2
    assert "Error" in result.stderr
    assert "Missing option '--out' / '-o'." in result.stderr


def test_no_overwrite(tmp_path):
    path = tmp_path / "diagram.png"
    path.touch()

    # With no-overwrite
    result = runner.invoke(
        app, ["erdantic.examples.pydantic.Quest", "-o", str(path), "--no-overwrite"]
    )
    print(result.output)
    assert result.exit_code == 1
    assert path.stat().st_size == 0

    # Overwrite
    result = runner.invoke(app, ["erdantic.examples.pydantic.Quest", "-o", str(path)])
    print(result.output)
    assert result.exit_code == 0
    assert path.stat().st_size > 0


def test_dot(tmp_path):
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party", "-d"])
    print(result.output)
    assert result.exit_code == 0
    assert erd.to_dot(Party).strip() == result.stdout.strip()

    path = tmp_path / "diagram.png"
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party", "-d", "-o", str(path)])
    print(result.output)
    assert result.exit_code == 0
    assert not path.exists()  # -o is ignored and no file created
    assert erd.to_dot(Party).strip() == result.stdout.strip()

    # python -m erdantic
    result = subprocess.run(
        ["python", "-m", "erdantic", "erdantic.examples.pydantic.Party", "-d"],
        capture_output=True,
        universal_newlines=True,
    )
    print(result.stderr)
    print(result.stdout)
    assert result.returncode == 0
    assert not path.exists()  # -o is ignored and no file created
    assert erd.to_dot(Party).strip() == result.stdout.strip()


def test_help():
    """Test the CLI with --help flag."""
    result = runner.invoke(app, ["--help"])
    print(result.output)
    assert result.exit_code == 0
    assert (
        "Draw entity relationship diagrams (ERDs) for Python data model classes." in result.output
    )


def test_version():
    """Test the CLI with --version flag."""
    result = runner.invoke(app, ["--version"])
    print(result.output)
    assert result.exit_code == 0
    assert result.output.strip() == __version__
