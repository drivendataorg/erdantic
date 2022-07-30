from enum import Enum
from importlib import import_module
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

import typer

from erdantic.base import model_adapter_registry
from erdantic.erd import create
from erdantic.exceptions import ModelOrModuleNotFoundError
from erdantic.version import __version__


app = typer.Typer()


class StrEnum(str, Enum):
    pass


if TYPE_CHECKING:
    # mypy typechecking doesn't really support enums created with functional API
    # https://github.com/python/mypy/issues/6037

    class SupportedModelIdentifier(StrEnum):
        pass

else:
    SupportedModelIdentifier = StrEnum(
        "SupportedModelIdentifier", {key: key for key in model_adapter_registry.keys()}
    )


def version_callback(version: bool):
    """Print erdantic version to console."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


def dot_callback(ctx: typer.Context, dot: bool):
    """Set --out to not be required since we're going to ignore it."""
    if dot:
        for param in ctx.command.params:
            if param.name == "out":
                param.required = False
    return dot


@app.command()
def main(
    models_or_modules: List[str] = typer.Argument(
        ...,
        help=(
            "One or more full dotted paths for data model classes, or modules containing data "
            "model classes, to include in diagram, e.g., 'erdantic.examples.pydantic.Party'. Only "
            "the root models of composition trees are needed; erdantic will traverse the "
            "composition tree to find component classes."
        ),
    ),
    termini: List[str] = typer.Option(
        None,
        "--terminus",
        "-t",
        help=(
            "Full dotted paths for data model classes to set as terminal nodes in the diagram. "
            "erdantic will stop searching for component classes when it reaches these models. "
            "Repeat this option if more than one."
        ),
    ),
    limit_search_models_to: List[SupportedModelIdentifier] = typer.Option(
        None,
        "--limit-search-models-to",
        "-m",
        help=(
            "Identifiers of model classes that erdantic supports. If any are specified, when "
            "searching a module, limit data model classes to those ones. Repeat this option if "
            "more than one.Defaults to None which will find all data model classes supported by "
            "erdantic. "
        ),
    ),
    out: Path = typer.Option(..., "--out", "-o", help="Output filename."),
    dot: Optional[bool] = typer.Option(
        None,
        "--dot",
        "-d",
        callback=dot_callback,
        help=(
            "Print out Graphviz DOT language representation for generated graph to console "
            "instead of rendering an image. The --out option will be ignored."
        ),
    ),
    no_overwrite: Optional[bool] = typer.Option(
        None, "--no-overwrite", help="Prevent overwriting an existing file."
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show erdantic version and exit.",
    ),
):
    """Draw entity relationship diagrams (ERDs) for Python data model classes. Diagrams are
    rendered using the Graphviz library. Currently supported data modeling frameworks are Pydantic
    and standard library dataclasses.
    """
    model_or_module_objs = [import_object_from_name(mm) for mm in models_or_modules]
    termini_classes = [import_object_from_name(mm) for mm in termini]
    limit_search_models_to_str = [
        m.value for m in limit_search_models_to
    ] or None  # Don't want empty list
    diagram = create(
        *model_or_module_objs,
        termini=termini_classes,
        limit_search_models_to=limit_search_models_to_str,
    )
    if dot:
        typer.echo(diagram.to_dot())
    else:
        if out.exists() and no_overwrite:
            typer.echo(f"{out} already exists, and you specified --no-overwrite.")
            raise typer.Exit(code=1)
        diagram.draw(out)
        typer.echo(f"Rendered diagram to {out}")


def import_object_from_name(full_obj_name):
    # Try to import as a module
    try:
        return import_module(full_obj_name)
    except ModuleNotFoundError:
        try:
            module_name, obj_name = full_obj_name.rsplit(".", 1)
            module = import_module(module_name)
            return getattr(module, obj_name)
        except (ImportError, AttributeError):
            raise ModelOrModuleNotFoundError(f"{full_obj_name} not found")
