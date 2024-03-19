from pathlib import Path
import platform

import nox


@nox.session(venv_backend="mamba|conda", python="3.11", reuse_venv=True)
def dev(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    session.install("-r", "requirements/dev.txt")


@nox.session(venv_backend="uv|virtualenv", python="3.11", reuse_venv=True)
def lint(session):
    session.env.pop("CONDA_PREFIX", None)  # uv errors if both venv and conda env are active
    session.install("-r", "requirements/lint.txt")
    session.run("ruff", "format", "--check")
    session.run("ruff", "check")


@nox.session(venv_backend="uv|virtualenv", python="3.11", reuse_venv=True)
def typecheck(session):
    session.env.pop("CONDA_PREFIX", None)  # uv errors if both venv and conda env are active
    session.install("-r", "requirements/typecheck.txt")
    session.run("mypy")


@nox.session(
    venv_backend="mamba|conda",
    python=["3.8", "3.9", "3.10", "3.11", "3.12"],
    reuse_venv=True,
)
def tests(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    session.install("-r", "requirements/tests.txt")
    session.run("pytest", "-vv")


@nox.session(venv_backend="uv|virtualenv", reuse_venv=True)
def build(session):
    session.env.pop("CONDA_PREFIX", None)  # uv errors if both venv and conda env are active
    session.install("build")
    session.run("python", "-m", "build")


@nox.session(
    venv_backend="mamba|conda",
    python=["3.8", "3.9", "3.10", "3.11", "3.12"],
    reuse_venv=False,
)
def test_wheel(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    wheel_path = next(Path("dist").glob("*.whl")).resolve()
    session.install(wheel_path)
    session.run("erdantic", "--version")


@nox.session(
    venv_backend="mamba|conda",
    python=["3.8", "3.9", "3.10", "3.11", "3.12"],
    reuse_venv=False,
)
def test_sdist(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    sdist_path = next(Path("dist").glob("*.tar.gz")).resolve()
    session.install(sdist_path)
    session.run("erdantic", "--version")


@nox.session(venv_backend="mamba|conda", python="3.11", reuse_venv=True)
def docs(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    session.install("-r", "requirements/docs.txt")
    session.run("make", "docs")
