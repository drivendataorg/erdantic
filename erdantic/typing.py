import collections.abc
from typing import (
    Any,
    ForwardRef,
    List,
    Literal,
    Optional,
    Union,
    get_args,
    get_origin,
)

# Note Python 3.9's types.GenericAlias != typing._GenericAlias
# We still want typing._GenericAlias for typing module's deprecated capital generic aliases
from typing import _GenericAlias as GenericAlias  # type: ignore # Python 3.7+

from typenames import BaseNode, GenericNode, parse_type_tree

from erdantic.exceptions import _StringForwardRefError, _UnevaluatedForwardRefError


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


def is_many(tp: Union[type, GenericAlias], target: type) -> bool:
    """Given a type annotation `tp`, returns True if it represents a collection of many elements of
    the target type.

    Args:
        tp (Union[type, GenericAlias]): Type annotation
        target (Union[type, GenericAlias]): Type to check for many-ness

    Returns:
        bool: Result of check
    """
    root = parse_type_tree(tp)
    return _walk_type_tree(root, target)


def is_nullable(tp: Union[type, GenericAlias]) -> bool:
    """Given a type annotation, returns True if it is the typing.Optional type, meaning that a
    value of None is accepted.

    Args:
        tp (Union[type, GenericAlias]): Type annotation

    Returns:
        bool: Result of check
    """
    return get_origin(tp) is Union and type(None) in get_args(tp)


def get_depth1_bases(tp: type) -> List[type]:
    """Returns depth-1 base classes of a type."""
    bases_of_bases = {bb for b in tp.__mro__[1:] for bb in b.__mro__[1:]}
    return [b for b in tp.__mro__[1:] if b not in bases_of_bases]


def get_recursive_args(tp: Union[type, GenericAlias]) -> List[type]:
    """Recursively finds leaf-node types of possibly-nested generic type."""

    def recurse(t):
        if isinstance(t, str):
            raise _StringForwardRefError(forward_ref=t)
        elif isinstance(t, ForwardRef):
            if t.__forward_evaluated__:
                t = t.__forward_value__
            else:
                raise _UnevaluatedForwardRefError(forward_ref=t)

        args = get_args(t)
        is_literal = Literal is not None and get_origin(t) is Literal
        if is_literal:
            yield Literal
        elif args:
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
