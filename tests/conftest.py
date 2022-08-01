import pytest


@pytest.fixture(autouse=True)
def disable_typer_rich_colors(monkeypatch):
    # https://rich.readthedocs.io/en/stable/console.html#environment-variables
    monkeypatch.setenv("TERM", "unknown")
