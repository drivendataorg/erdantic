from enum import Enum
from importlib import import_module
import logging
from pathlib import Path
import sys
from types import ModuleType
from typing import TYPE_CHECKING, List, Optional, Union

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

import typer

from erdantic._logging import package_logger
from erdantic._version import __version__
from erdantic.convenience import create
from erdantic.exceptions import ModelOrModuleNotFoundError
from erdantic.plugins import list_plugins

app = typer.Typer()

logger = logging.getLogger(__name__)


class StrEnum(str, Enum):
    pass


if TYPE_CHECKING:
    # mypy typechecking doesn't support enums created with functional API
    # https://github.com/python/mypy/issues/6037

    class AvailablePluginKeys(StrEnum): ...

else:
    AvailablePluginKeys = StrEnum("AvailablePluginKeys", {key: key for key in list_plugins()})


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
    models_or_modules: Annotated[
        List[str],
        typer.Argument(
            help=(
                "One or more full dotted paths for data model classes, or modules containing data "
                "model classes, to include in diagram, e.g., 'erdantic.examples.pydantic.Party'. "
                "Only the root models of composition trees are needed; erdantic will traverse the "
                "composition tree to find component classes."
            ),
        ),
    ],
    out: Annotated[
        Path,
        typer.Option("--out", "-o", help="Output filename."),
    ],
    terminal_models: Annotated[
        List[str],
        typer.Option(
            "--terminal-model",
            "-t",
            help=(
                "Full dotted paths for data model classes to set as terminal nodes in the "
                "diagram. erdantic will stop searching for component classes when it reaches "
                "these models. Repeat this option if more than one."
            ),
        ),
    ] = [],
    termini: Annotated[
        List[str],
        typer.Option(
            "--terminus",
            help=("Deprecated. Use --terminal-model instead."),
        ),
    ] = [],
    limit_search_models_to: Annotated[
        List[AvailablePluginKeys],
        typer.Option(
            "--limit-search-models-to",
            "-m",
            help=(
                "Plugin identifiers. If any are specified, when "
                "searching a module, limit data model classes to those ones. Repeat this option "
                "if more than one. Defaults to None which will find data model classes "
                "matching any active plugin. "
            ),
        ),
    ] = [],
    dot: Annotated[
        bool,
        typer.Option(
            "--dot",
            "-d",
            callback=dot_callback,
            help=(
                "Print out Graphviz DOT language representation for generated graph to console "
                "instead of rendering an image. The --out option will be ignored."
            ),
        ),
    ] = False,
    no_overwrite: Annotated[
        bool,
        typer.Option("--no-overwrite", help="Prevent overwriting an existing file."),
    ] = False,
    quiet: Annotated[
        int,
        typer.Option(
            "--quiet",
            "-q",
            count=True,
            show_default=False,
            help="Use to decrease log verbosity. Can use multiple times.",
        ),
    ] = 0,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            show_default=False,
            help="Use to increase log verbosity. Can use multiple times.",
        ),
    ] = 0,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show erdantic version and exit.",
        ),
    ] = None,
):
    """Draw entity relationship diagrams (ERDs) for Python data model classes. Diagrams are
    rendered using the Graphviz library. Currently supported data modeling frameworks are Pydantic,
    attrs, and standard library dataclasses.
    """
    # Set up logger
    log_level = logging.INFO + 10 * quiet - 10 * verbose
    package_logger.setLevel(log_level)
    log_handler = logging.StreamHandler()
    package_logger.addHandler(log_handler)
    log_formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    log_handler.setFormatter(log_formatter)

    logger.debug("Registered plugins: %s", ", ".join(list_plugins()))

    logger.debug("models_or_modules: %s", models_or_modules)
    logger.debug("out: %s", out)
    logger.debug("terminal_models: %s", terminal_models)
    logger.debug("termini: %s", termini)
    logger.debug("limit_search_models_to: %s", limit_search_models_to)
    logger.debug("dot: %s", dot)
    logger.debug("no_overwrite: %s", no_overwrite)

    model_or_module_objs = [import_object_from_name(mm) for mm in models_or_modules]
    terminal_model_classes = [import_object_from_name(mm) for mm in terminal_models]
    termini_classes = [import_object_from_name(mm) for mm in termini]
    limit_search_models_to_str = [
        m.value for m in limit_search_models_to
    ] or None  # Don't want empty list
    diagram = create(
        *model_or_module_objs,  # type: ignore [arg-type]
        terminal_models=terminal_model_classes,  # type: ignore [arg-type]
        termini=termini_classes,  # type: ignore [arg-type]
        limit_search_models_to=limit_search_models_to_str,
    )
    if dot:
        typer.echo(diagram.to_dot())
    else:
        if out.exists() and no_overwrite:
            logger.error(f"{out} already exists, and you specified --no-overwrite.")
            raise typer.Exit(code=1)
        diagram.draw(out)
        logger.info(f"Rendered diagram to {out}")


def import_object_from_name(full_obj_name: str) -> Union[ModuleType, object]:
    """Import an object from a fully qualified name."""
    try:
        # Try to import as a module
        return import_module(full_obj_name)
    except ModuleNotFoundError:
        # Try to import as an object in a module
        try:
            module_name, obj_name = full_obj_name.rsplit(".", 1)
            module = import_module(module_name)
            return getattr(module, obj_name)
        except (ImportError, AttributeError) as e:
            raise ModelOrModuleNotFoundError(
                f"Unable to import '{full_obj_name}'.", name=full_obj_name, path=__file__
            ) from e
        except ValueError as e:
            # This can happen if there are no dots in the name
            if "not enough values to unpack (expected 2, got 1)" in str(e):
                raise ModelOrModuleNotFoundError(
                    f"Unable to import '{full_obj_name}'. "
                    "It should be a fully qualified name for a model class or module.",
                    name=full_obj_name,
                    path=__file__,
                )
            else:
                raise e
