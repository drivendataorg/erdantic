from typing import Optional

from attrs import define, resolve_types
import pytest

from erdantic.core import FullyQualifiedName
import erdantic.examples.attrs as attrs_examples
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins.attrs import (
    get_fields_from_attrs_class,
    is_attrs_class,
)


def test_is_pydantic_model():
    class NotAPydanticModel:
        pass

    assert is_attrs_class(attrs_examples.Party)
    assert is_attrs_class(attrs_examples.QuestGiver)
    assert not is_attrs_class(
        attrs_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_attrs_class("Hello")
    assert not is_attrs_class(str)
    assert not is_attrs_class(NotAPydanticModel)


def test_get_fields_from_attrs_class():
    fields = get_fields_from_attrs_class(attrs_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(attrs_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(attrs_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(attrs_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "List[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(attrs_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"


@define
class HasForwardRefs:
    fwd_ref: "attrs_examples.Party"
    nested_fwd_ref: Optional["attrs_examples.Quest"]
    self_fwd_ref: "HasForwardRefs"
    nested_self_fwd_ref: Optional["HasForwardRefs"]


def test_forward_references():
    fields = {fi.name: fi for fi in get_fields_from_attrs_class(HasForwardRefs)}
    print(fields)
    assert fields["fwd_ref"].type_name == "Party"
    assert fields["fwd_ref"].raw_type == attrs_examples.Party
    assert fields["nested_fwd_ref"].type_name == "Optional[Quest]"
    assert fields["nested_fwd_ref"].raw_type == Optional[attrs_examples.Quest]
    assert fields["self_fwd_ref"].type_name == "HasForwardRefs"
    assert fields["self_fwd_ref"].raw_type == HasForwardRefs
    assert fields["nested_self_fwd_ref"].type_name == "Optional[HasForwardRefs]"
    assert fields["nested_self_fwd_ref"].raw_type == Optional[HasForwardRefs]

    # Class is defined in a function scope
    @define
    class FnScopeHasForwardRefs:
        fwd_ref: "attrs_examples.Party"
        nested_fwd_ref: Optional["attrs_examples.Quest"]
        global_fwd_ref: "HasForwardRefs"
        nested_global_fwd_ref: Optional["HasForwardRefs"]
        fwd_ref_of_local: "FnScopeHasForwardRefs"
        nested_fwd_ref_of_local: Optional["FnScopeHasForwardRefs"]

    resolve_types(FnScopeHasForwardRefs, globalns=globals(), localns=locals())

    fields = {fi.name: fi for fi in get_fields_from_attrs_class(FnScopeHasForwardRefs)}
    print(fields)
    assert fields["fwd_ref"].type_name == "Party"
    assert fields["fwd_ref"].raw_type == attrs_examples.Party
    assert fields["nested_fwd_ref"].type_name == "Optional[Quest]"
    assert fields["nested_fwd_ref"].raw_type == Optional[attrs_examples.Quest]
    assert fields["global_fwd_ref"].type_name == "HasForwardRefs"
    assert fields["global_fwd_ref"].raw_type == HasForwardRefs
    assert fields["nested_global_fwd_ref"].type_name == "Optional[HasForwardRefs]"
    assert fields["nested_global_fwd_ref"].raw_type == Optional[HasForwardRefs]
    assert fields["fwd_ref_of_local"].type_name == "FnScopeHasForwardRefs"
    assert fields["fwd_ref_of_local"].raw_type == FnScopeHasForwardRefs
    assert fields["nested_fwd_ref_of_local"].type_name == "Optional[FnScopeHasForwardRefs]"
    assert fields["nested_fwd_ref_of_local"].raw_type == Optional[FnScopeHasForwardRefs]


def test_forward_ref_of_local_class_unresolved():
    @define
    class FnScopeHasForwardRefsUnresolved:
        fwd_ref_of_local: "FnScopeHasForwardRefsUnresolved"

    with pytest.raises(UnresolvableForwardRefError):
        _ = {fi.name: fi for fi in get_fields_from_attrs_class(FnScopeHasForwardRefsUnresolved)}
