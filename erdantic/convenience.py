import inspect
import logging
import os
from types import ModuleType
from typing import Any, Collection, Iterator, Mapping, Optional, Union
import warnings

from erdantic.core import EntityRelationshipDiagram
from erdantic.plugins import get_predicate_fn, list_plugins

logger = logging.getLogger(__name__)


def create(
    *models_or_modules: Union[type, ModuleType],
    terminal_models: Collection[type] = tuple(),
    termini: Collection[type] = tuple(),
    limit_search_models_to: Optional[Collection[str]] = None,
) -> EntityRelationshipDiagram:
    """Construct [`EntityRelationshipDiagram`][erdantic.erd.EntityRelationshipDiagram] from given
    data model classes or modules.

    Args:
        *models_or_modules (type | ModuleType): Data model classes to add to diagram, or modules
            to search for data model classes.
        terminal_models (Collection[type]): Data model classes to set as terminal nodes. erdantic
            will stop searching for component classes when it reaches these models
        termini (Collection[type]): Deprecated. Use `terminal_models` instead.
        limit_search_models_to (Collection[str] | None): Plugin identifiers to limit to when
            searching modules for data model classes. Defaults to None which will not impose any
            limits.
    Raises:
        UnknownModelTypeError: If model is not recognized as a supported model type.
        PluginNotFoundError: If a plugin key does not match any registered plugins.

    Returns:
        EntityRelationshipDiagram: diagram object for given data model.
    """
    if termini:
        warnings.warn(
            "The 'termini' argument is deprecated and will be removed in a future release. "
            "Please use 'terminal_models' instead.",
            DeprecationWarning,
        )
        if terminal_models:
            raise ValueError(
                "Cannot specify both 'terminal_models' and 'termini' at the same time."
            )
        terminal_models = termini

    diagram = EntityRelationshipDiagram()

    # Add terminal models and don't recurse
    for model in terminal_models:
        diagram.add_model(model, recurse=False)

    for mm in models_or_modules:
        if isinstance(mm, ModuleType):
            logger.debug("Searching input module '%s' for data model classes", mm.__name__)
            for member in find_models(mm, limit_search_models_to=limit_search_models_to):
                diagram.add_model(member)
        else:
            diagram.add_model(mm)
    return diagram


def find_models(
    module: ModuleType, limit_search_models_to: Optional[Collection[str]] = None
) -> Iterator[type]:
    """Searches a module and yields all data model classes found.

    Args:
        module (ModuleType): Module to search for data model classes.
        limit_search_models_to (Collection[str] | None): Plugin identifiers to limit to when
            searching modules for data model classes. Defaults to None which will not impose any
            limits.

    Yields:
        Iterator[type]: Members of module that are data model classes.
    """
    all_plugins = list_plugins()
    if limit_search_models_to is not None:
        predicate_fns = [get_predicate_fn(key) for key in limit_search_models_to]
    else:
        predicate_fns = [get_predicate_fn(key) for key in all_plugins]
    for _, member in inspect.getmembers(module, inspect.isclass):
        if member.__module__ == module.__name__:
            for predicate_fn in predicate_fns:
                if predicate_fn(member):
                    logger.debug(
                        "Found data model class '%s' in module '%s'", member, module.__name__
                    )
                    yield member


def draw(
    *models_or_modules: Union[type, ModuleType],
    out: Union[str, os.PathLike],
    terminal_models: Collection[type] = tuple(),
    termini: Collection[type] = tuple(),
    limit_search_models_to: Optional[Collection[str]] = None,
    graph_attrs: Optional[Mapping[str, Any]] = None,
    node_attrs: Optional[Mapping[str, Any]] = None,
    edge_attrs: Optional[Mapping[str, Any]] = None,
    **kwargs,
):
    """Render entity relationship diagram for given data model classes to file.

    Args:
        *models_or_modules (type | ModuleType): Data model classes to add to diagram, or modules
            to search for data model classes.
        terminal_models (Collection[type]): Data model classes to set as terminal nodes. erdantic
            will stop searching for component classes when it reaches these models
        termini (Collection[type]): Deprecated. Use `terminal_models` instead.
        limit_search_models_to (Optional[Collection[str]]): Plugin identifiers to limit to when
            searching modules for data model classes. Defaults to None which will not impose any
            limits.
        graph_attrs (Mapping[str, Any] | None, optional): Override any graph attributes on
            the `pygraphviz.AGraph` instance. Defaults to None.
        node_attrs (Mapping[str, Any] | None, optional): Override any node attributes for all
            nodes on the `pygraphviz.AGraph` instance. Defaults to None.
        edge_attrs (Mapping[str, Any] | None, optional): Override any edge attributes for all
            edges on the `pygraphviz.AGraph` instance. Defaults to None.
        **kwargs: Additional keyword arguments to [`pygraphviz.AGraph.draw`](https://pygraphviz.github.io/documentation/latest/reference/agraph.html#pygraphviz.AGraph.draw).

    Raises:
        UnknownModelTypeError: If model is not recognized as a supported model type.
        PluginNotFoundError: If a plugin key does not match any registered plugins.
    """
    diagram = create(
        *models_or_modules,
        terminal_models=terminal_models,
        limit_search_models_to=limit_search_models_to,
    )
    diagram.draw(
        out=out, graph_attrs=graph_attrs, node_attrs=node_attrs, edge_attrs=edge_attrs, **kwargs
    )


def to_dot(
    *models_or_modules: Union[type, ModuleType],
    terminal_models: Collection[type] = [],
    limit_search_models_to: Optional[Collection[str]] = None,
    graph_attrs: Optional[Mapping[str, Any]] = None,
    node_attrs: Optional[Mapping[str, Any]] = None,
    edge_attrs: Optional[Mapping[str, Any]] = None,
) -> str:
    """Generate Graphviz [DOT language](https://graphviz.org/doc/info/lang.html) representation of
    entity relationship diagram for given data model classes.

    Args:
        *models_or_modules (type | ModuleType): Data model classes to add to diagram, or modules
            to search for data model classes.
        terminal_models (Collection[type]): Data model classes to set as terminal nodes. erdantic
            will stop searching for component classes when it reaches these models
        termini (Collection[type]): Deprecated. Use `terminal_models` instead.
        limit_search_models_to (Optional[Collection[str]]): Plugin identifiers to limit to when
            searching modules for data model classes. Defaults to None which will not impose any
            limits.
        graph_attrs (Mapping[str, Any] | None, optional): Override any graph attributes on
            the `pygraphviz.AGraph` instance. Defaults to None.
        node_attrs (Mapping[str, Any] | None, optional): Override any node attributes for all
            nodes on the `pygraphviz.AGraph` instance. Defaults to None.
        edge_attrs (Mapping[str, Any] | None, optional): Override any edge attributes for all
            edges on the `pygraphviz.AGraph` instance. Defaults to None.

    Returns:
        str: DOT language representation of diagram
    """
    diagram = create(
        *models_or_modules,
        terminal_models=terminal_models,
        limit_search_models_to=limit_search_models_to,
    )
    return diagram.to_dot(graph_attrs=graph_attrs, node_attrs=node_attrs, edge_attrs=edge_attrs)