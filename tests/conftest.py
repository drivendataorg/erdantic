from pathlib import Path
import shutil

import pytest

import erdantic as erd
import erdantic.core

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


@pytest.fixture()
def version_patch(monkeypatch):
    """Monkeypatch version to stable value to compare with static test assets."""
    default_graph_attr = dict(erdantic.core.DEFAULT_GRAPH_ATTR)
    default_graph_attr["label"] = default_graph_attr["label"].replace(
        f"v{erdantic.__version__}", "vTEST"
    )
    monkeypatch.setattr(erdantic.core, "DEFAULT_GRAPH_ATTR", tuple(default_graph_attr.items()))

    monkeypatch.setattr(erd, "__version__", "TEST")
    monkeypatch.setattr(erdantic._version, "__version__", "TEST")
    monkeypatch.setattr(erdantic.core, "__version__", "TEST")
