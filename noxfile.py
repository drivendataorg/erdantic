from pathlib import Path

import nox


@nox.session(python="3.11", reuse_venv=True)
def dev(session):
    session.conda_install("graphviz", channel="conda-forge")
    session.install("-r", "requirements/dev.txt")


@nox.session(venv_backend="uv|virtualenv", python="3.11", reuse_venv=True)
def lint(session):
    session.install("-r", "requirements/lint.txt")
    session.run("ruff", "format", "--check")
    session.run("ruff", "check")


@nox.session(venv_backend="uv|virtualenv", python="3.11", reuse_venv=True)
def typecheck(session):
    session.install("-r", "requirements/typecheck.txt")
    session.run("mypy")


@nox.session(
    venv_backend="mamba|conda",
    python=["3.8", "3.9", "3.10", "3.11", "3.12"],
    reuse_venv=True,
)
def tests(session):
    session.conda_install("graphviz", channel="conda-forge")
    session.install("-r", "requirements/tests.txt")
    session.run("pytest", "-vv")


@nox.session(
    venv_backend="uv|virtualenv",
    python=["3.8", "3.9", "3.10", "3.11", "3.12"],
    reuse_venv=False,
)
def test_wheel(session):
    session.install("build")
    session.run("python", "-m", "build")
    wheel_path = next(Path("dist").glob("*.whl"))
    session.install(f"erdantic@{wheel_path}")
    session.run("erdantic", "--version")


@nox.session(
    venv_backend="uv|virtualenv",
    python=["3.8", "3.9", "3.10", "3.11", "3.12"],
    reuse_venv=False,
)
def test_sdist(session):
    session.install("build")
    session.run("python", "-m", "build")
    sdist_path = next(Path("dist").glob("*.tar.gz"))
    session.install(f"erdantic@{sdist_path}")
    session.run("erdantic", "--version")


@nox.session(
    venv_backend="uv|virtualenv",
    python="3.11",
    reuse_venv=True,
)
def docs(session):
    session.install("-r", "requirements/docs.txt")
    session.run("make", "docs")
