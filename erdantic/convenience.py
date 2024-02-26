import inspect
import os
from types import ModuleType
from typing import Iterable, Optional, Sequence, Union
import warnings

from erdantic.core import EntityRelationshipDiagram
from erdantic.exceptions import NotATypeError


def create(
    *models_or_modules: Union[type, ModuleType],
    terminal_models: Sequence[type] = tuple(),
    termini: Sequence[type] = tuple(),
    limit_search_models_to: Optional[Iterable[str]] = None,
) -> EntityRelationshipDiagram:
    """Construct [`EntityRelationshipDiagram`][erdantic.erd.EntityRelationshipDiagram] from given
    data model classes.

    Args:
        *models_or_modules (type): Data model classes to diagram or modules containing them.
        terminal_models (Sequence[type]): Data model classes to set as terminal nodes. erdantic will stop
            searching for component classes when it reaches these models
        limit_search_models_to (Optional[Iterable[sr]], optional): Iterable of identifiers of data
            model classes that erdantic supports. If any are specified, when searching a module,
            limit data model classes to those ones. Defaults to None which will find all data model
            classes supported by erdantic.
    Raises:
        UnknownModelTypeError: If model is not recognized as a supported model type.

    Returns:
        EntityRelationshipDiagram: diagram object for given data model.
    """
    if termini:
        if terminal_models:
            raise ValueError("Cannot specify both terminal_models and termini")
        warnings.warn(
            "The 'termini' argument is deprecated and will be removed in a future release. "
            "Please use 'terminal_models' instead.",
            DeprecationWarning,
        )
        terminal_models = termini

    models = []
    for mm in models_or_modules:
        if isinstance(mm, type):
            models.append(mm)
        elif isinstance(mm, ModuleType):
            models.extend(find_models(mm, limit_search_models_to=limit_search_models_to))
        else:
            raise NotATypeError(f"Given model is not a type: {mm}")
    for terminal_model in tuple(terminal_models):
        if not isinstance(terminal_model, type):
            raise NotATypeError(f"Given terminal model is not a type: {terminal_model}")

    erd = EntityRelationshipDiagram()

    erd.add_model()

    for raw_model in models:
        erd.add_model(raw_model)
    return erd


def find_models(
    module: ModuleType, limit_search_models_to: Optional[Iterable[str]] = None
) -> Iterator[type]:
    """Searches a module and yields all data model classes found.

    Args:
        module (ModuleType): Module to search for data model classes
        limit_search_models_to (Optional[Iterable[str]], optional): Iterable of identifiers of data
            model class types that erdantic supports. If any are specified, when searching a module,
            limit data model classes to those ones. Defaults to None which will find all data model
            classes supported by erdantic.

    Yields:
        Iterator[type]: Members of module that are data model classes.
    """
    for _, member in inspect.getmembers(module, inspect.isclass):
        if member.__module__ == module.__name__:
            for model_adapter in limit_search_models_to_adapters:
                if model_adapter.is_model_type(member):
                    yield member


def draw(
    *models_or_modules: Union[type, ModuleType],
    out: Union[str, os.PathLike],
    terminal_models: Sequence[type] = tuple(),
    termini: Sequence[type] = tuple(),
    limit_search_models_to: Optional[Iterable[str]] = None,
    **kwargs,
):
    """Render entity relationship diagram for given data model classes to file.

    Args:
        *models_or_modules (type): Data model classes to diagram, or modules containing them.
        out (Union[str, os.PathLike]): Output file path for rendered diagram.
        terminal_models (Sequence[type]): Data model classes to set as terminal nodes. erdantic will stop
            searching for component classes when it reaches these models
        limit_search_models_to (Optional[Iterable[sr]], optional): Iterable of identifiers of data
            model classes that erdantic supports. If any are specified, when searching a module,
            limit data model classes to those ones. Defaults to None which will find all data model
            classes supported by erdantic.
        **kwargs: Additional keyword arguments to [`pygraphviz.AGraph.draw`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html#pygraphviz.AGraph.draw).
    """
    diagram = create(
        *models_or_modules,
        terminal_models=terminal_models,
        limit_search_models_to=limit_search_models_to,
    )
    diagram.draw(out=out, **kwargs)


def to_dot(
    *models_or_modules: Union[type, ModuleType],
    terminal_models: Sequence[type] = [],
    limit_search_models_to: Optional[Iterable[str]] = None,
) -> str:
    """Generate Graphviz [DOT language](https://graphviz.org/doc/info/lang.html) representation of
    entity relationship diagram for given data model classes.

    Args:
        *models_or_modules (type): Data model classes to diagram, or modules containing them.
        terminal_models (Sequence[type]): Data model classes to set as terminal nodes. erdantic will stop
            searching for component classes when it reaches these models
        limit_search_models_to (Optional[Iterable[sr]], optional): Iterable of identifiers of data
            model classes that erdantic supports. If any are specified, when searching a module,
            limit data model classes to those ones. Defaults to None which will find all data model
            classes supported by erdantic.

    Returns:
        str: DOT language representation of diagram
    """
    diagram = create(
        *models_or_modules,
        terminal_models=terminal_models,
        limit_search_models_to=limit_search_models_to,
    )
    return diagram.to_dot()
