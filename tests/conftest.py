from pathlib import Path
import shutil

import pytest

OUTPUTS_DIR = Path(__file__).resolve().parent / "_outputs"


@pytest.fixture(scope="session", autouse=True)
def outputs_dir():
    shutil.rmtree(OUTPUTS_DIR, ignore_errors=True)
    OUTPUTS_DIR.mkdir(parents=True)
    yield OUTPUTS_DIR


@pytest.fixture(autouse=True)
def disable_typer_rich_colors(monkeypatch):
    # https://rich.readthedocs.io/en/stable/console.html#environment-variables
    monkeypatch.setenv("TERM", "unknown")
