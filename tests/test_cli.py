import filecmp

from typer.testing import CliRunner

from erdantic.cli import app
from erdantic.erd import draw, to_dot
from erdantic.examples.pydantic import Party
from erdantic.version import __version__


runner = CliRunner()


def test_draw(tmp_path):
    path1 = tmp_path / "diagram1.png"
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party", "-o", str(path1)])
    assert result.exit_code == 0
    assert path1.exists()

    path2 = tmp_path / "diagram2.png"
    draw(Party, path=path2)
    assert path2.exists()

    assert filecmp.cmp(path1, path2)

    result = runner.invoke(app, ["erdantic.examples.pydantic.Quest", "-o", str(path1)])
    assert result.exit_code == 1
    assert filecmp.cmp(path1, path2)


def test_dot(tmp_path):
    path = tmp_path / "diagram.png"
    result = runner.invoke(app, ["erdantic.examples.pydantic.Party", "-d", "-o", str(path)])
    assert result.exit_code == 0
    assert not path.exists()  # -o is ignored and no file created
    assert to_dot(Party) in result.stdout


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
