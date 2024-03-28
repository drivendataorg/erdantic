import collections.abc
import sys
from typing import Any, ForwardRef, Iterator, List, Literal, TypeVar, Union, get_args, get_origin

from typenames import BaseNode, GenericNode, parse_type_tree

from erdantic.exceptions import _UnevaluatedForwardRefError

# TypeVar for type annotations
# Most typing special forms have type 'object'
# There is a stalled proposal for TypeForm: https://github.com/python/mypy/issues/9773
if sys.version_info >= (3, 10):
    from types import UnionType

    _TypeForm = TypeVar("_TypeForm", bound=type | UnionType | str | object)
else:
    _TypeForm = TypeVar("_TypeForm", bound=Union[type, str, object])


def _walk_type_tree(node: BaseNode, target: type) -> bool:
    """Recursively walk a type tree to check if type is many in target type."""
    if isinstance(node, GenericNode):
        if isinstance(node.origin, type) and (
            issubclass(node.origin, collections.abc.Container)
            or issubclass(node.origin, collections.abc.Iterable)
            or issubclass(node.origin, collections.abc.Sized)
        ):
            # Check recursive args for target type
            return target in get_recursive_args(node.tp)
        elif node.origin is Union:
            return any(_walk_type_tree(arg_node, target) for arg_node in node.arg_nodes)
    return False


def is_collection_type_of(tp: _TypeForm, target: type) -> bool:
    """Given a type annotation, returns True if it represents a collection of many elements of the
    target type.

    Args:
        tp (Union[type, GenericAlias]): Type annotation.
        target (type): Type to check for many-ness of.

    Returns:
        bool: Result of check.
    """
    root = parse_type_tree(tp)
    return _walk_type_tree(root, target)


def is_nullable_type(tp: _TypeForm) -> bool:
    """Given a type annotation, returns True if it is a union with None as a possible option,
    such as typing.Optional.

    Args:
        tp (Union[type, GenericAlias]): Type annotation.

    Returns:
        bool: Result of check.
    """
    return get_origin(tp) is Union and type(None) in get_args(tp)


def get_depth1_bases(tp: type) -> List[type]:
    """Returns depth-1 base classes of a type."""
    bases_of_bases = {bb for b in tp.__mro__[1:] for bb in b.__mro__[1:]}
    return [b for b in tp.__mro__[1:] if b not in bases_of_bases]


def get_recursive_args(tp: _TypeForm) -> List[_TypeForm]:
    """Recursively finds leaf-node types of possibly-nested generic type."""

    def recurse(t: _TypeForm) -> Iterator[_TypeForm]:
        if isinstance(t, str):
            raise _UnevaluatedForwardRefError(forward_ref=t)
        elif isinstance(t, ForwardRef):
            if t.__forward_evaluated__:
                t = t.__forward_value__  # type: ignore [assignment]
            else:
                raise _UnevaluatedForwardRefError(forward_ref=t.__forward_arg__)

        if get_origin(t) is Literal:
            yield t
            return

        args = get_args(t)
        if args:
            for arg in args:
                yield from recurse(arg)
        else:
            yield t

    return list(recurse(tp))


def repr_type_with_mro(obj: Any) -> str:
    """Return MRO of object if it has one. Otherwise return its repr."""

    def _full_name(tp: type) -> str:
        module = tp.__module__
        return f"{module}.{tp.__qualname__}".replace("builtins.", "")

    if hasattr(obj, "__mro__"):
        mro = ", ".join(_full_name(m) for m in obj.__mro__)
        return f"<mro ({mro})>"
    return repr(obj)
