import filecmp
import subprocess

from typer.testing import CliRunner

import erdantic as erd
from erdantic.cli import app
from erdantic.examples.pydantic import Party
from erdantic.version import __version__


runner = CliRunner()


def test_draw(tmp_path):
    # With library for comparison
    path_base = tmp_path / "diagram_base.png"
    erd.draw(Party, out=path_base)
    assert path_base.exists()

    # With CLI
    path1 = tmp_path / "diagram1.png"
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party", "-o", str(path1)])
    assert result.exit_code == 0
    assert path1.exists()
    assert filecmp.cmp(path1, path_base)

    # python -m erdantic
    path2 = tmp_path / "diagram2.png"
    result = subprocess.run(
        ["python", "-m", "erdantic", "erdantic.examples.pydantic.Party", "-o", str(path2)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert result.returncode == 0
    assert path2.exists()
    assert filecmp.cmp(path2, path_base)


def test_missing_out(tmp_path):
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party"])
    assert result.exit_code == 2
    assert "Error: Missing option '--out' / '-o'." in result.stdout


def test_no_overwrite(tmp_path):
    path = tmp_path / "diagram.png"
    path.touch()

    # With no-overwrite
    result = runner.invoke(
        app, ["erdantic.examples.pydantic.Quest", "-o", str(path), "--no-overwrite"]
    )
    assert result.exit_code == 1
    assert path.stat().st_size == 0

    # Overwrite
    result = runner.invoke(app, ["erdantic.examples.pydantic.Quest", "-o", str(path)])
    assert result.exit_code == 0
    assert path.stat().st_size > 0


def test_dot(tmp_path):
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party", "-d"])
    assert result.exit_code == 0
    assert erd.to_dot(Party).strip() == result.stdout.strip()

    path = tmp_path / "diagram.png"
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party", "-d", "-o", str(path)])
    assert result.exit_code == 0
    assert not path.exists()  # -o is ignored and no file created
    assert erd.to_dot(Party).strip() == result.stdout.strip()

    # python -m erdantic
    result = subprocess.run(
        ["python", "-m", "erdantic", "erdantic.examples.pydantic.Party", "-d"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    assert result.returncode == 0
    assert not path.exists()  # -o is ignored and no file created
    assert erd.to_dot(Party).strip() == result.stdout.strip()


def test_help():
    """Test the CLI with --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert (
        "Draw entity relationship diagrams (ERDs) for Python data model classes." in result.output
    )


def test_version():
    """Test the CLI with --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__
