from pathlib import Path
import platform
import shutil

import nox


def find_uv() -> tuple[bool, str]:
    # Inspired by:
    # https://github.com/wntrblm/nox/blob/08813c3c6b0d2171c280bbfcf219d089a16d1ac2/nox/virtualenv.py#L42
    uv = shutil.which("uv")
    if uv is not None:
        return True, uv
    return False, "uv"


HAS_UV, UV = find_uv()


@nox.session(venv_backend="mamba|conda", python="3.11", reuse_venv=True)
def dev(session):
    """Set up a development environment."""
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    if HAS_UV:
        session.run(UV, "pip", "install", "-r", "requirements/dev.txt", external=True)
    else:
        session.install("-r", "requirements/dev.txt")
    conda_cmd = session.virtualenv.conda_cmd
    env_path = Path(session.virtualenv.location).relative_to(Path.cwd())
    session.log(f"Activate with: {conda_cmd} activate {env_path}")


@nox.session(venv_backend="uv|virtualenv", python="3.11", reuse_venv=True)
def lint(session):
    session.env.pop("CONDA_PREFIX", None)  # uv errors if both venv and conda env are active
    session.install("-r", "requirements/lint.txt")
    session.run("ruff", "format", "--check")
    session.run("ruff", "check")


@nox.session(venv_backend="mamba|conda", python="3.11", reuse_venv=True)
def typecheck(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    if HAS_UV:
        session.run(UV, "pip", "install", "-r", "requirements/typecheck.txt", external=True)
    else:
        session.install("-r", "requirements/typecheck.txt")
    session.run("mypy", "--install-types", "--non-interactive")


@nox.session(
    venv_backend="mamba|conda",
    python=["3.8", "3.9", "3.10", "3.11", "3.12"],
    reuse_venv=True,
)
def tests(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    if HAS_UV:
        session.run(UV, "pip", "install", "-r", "requirements/tests.txt", external=True)
    else:
        session.install("-r", "requirements/tests.txt")
    session.run("pytest", "-vv")


@nox.session(venv_backend="uv|virtualenv", reuse_venv=True)
def build(session):
    session.env.pop("CONDA_PREFIX", None)  # uv errors if both venv and conda env are active
    session.install("build")
    session.run("python", "-m", "build")


@nox.session(venv_backend="mamba|conda", python="3.12", reuse_venv=False)
@nox.parametrize("extras", ["", "[attrs]"])
def test_wheel(session, extras):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    wheel_path = next(Path("dist").glob("*.whl")).resolve()
    if HAS_UV:
        session.run(UV, "pip", "install", f"erdantic{extras} @ {wheel_path}", external=True)
    else:
        session.install(str(wheel_path) + extras)
    session.run("python", "-m", "erdantic", "--version")
    session.run("python", "-c", "import erdantic; print(erdantic.list_plugins())")


@nox.session(venv_backend="mamba|conda", python="3.12", reuse_venv=False)
def test_sdist(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    sdist_path = next(Path("dist").glob("*.tar.gz")).resolve()
    if HAS_UV:
        session.run(UV, "pip", "install", f"erdantic @ {sdist_path}", external=True)
    else:
        session.install(sdist_path)
    session.run("python", "-m", "erdantic", "--version")


@nox.session(venv_backend="mamba|conda", python="3.11", reuse_venv=True)
def docs(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    if HAS_UV:
        session.run(UV, "pip", "install", "-r", "requirements/docs.txt", external=True)
    else:
        session.install("-r", "requirements/docs.txt")
    with session.chdir("docs"):
        session.run("mkdocs", "build")


@nox.session(venv_backend="mamba|conda", python="3.11", reuse_venv=True)
def docs_serve(session):
    session.conda_install("graphviz", channel="conda-forge")
    if platform.system() == "Windows":
        session.conda_install("pygraphviz", channel="conda-forge")
    if HAS_UV:
        session.run(UV, "pip", "install", "-r", "requirements/docs.txt", external=True)
    else:
        session.install("-r", "requirements/docs.txt")
    with session.chdir("docs"):
        session.run("mkdocs", "serve")
