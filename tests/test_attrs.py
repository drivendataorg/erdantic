from pprint import pprint
from typing import Optional

from attrs import define, resolve_types
import pytest

from erdantic.core import EntityRelationshipDiagram, FullyQualifiedName
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
class GlobalOtherClassBefore:
    """Another attrs class to be referenced as a forward reference. Defined before the class that
    references it."""

    my_field: str


@define
class GlobalWithFwdRefs:
    """Globally defined attrs class with forward references. This should have no problems being
    automatically resolved."""

    # Resolved by attrs.resolve_types() in  get_fields_from_attrs_class
    imported_ref: "attrs_examples.Party"
    nested_imported_ref: Optional["attrs_examples.Quest"]
    self_ref: "GlobalWithFwdRefs"
    nested_self_ref: Optional["GlobalWithFwdRefs"]
    global_ref_before: "GlobalOtherClassBefore"
    nested_global_ref_before: Optional["GlobalOtherClassBefore"]
    global_ref_after: "GlobalOtherClassAfter"
    nested_global_ref_after: Optional["GlobalOtherClassAfter"]


@define
class GlobalOtherClassAfter:
    """Another attrs class to be referenced as a forward reference. Defined after the class that
    references it."""

    my_field: str


def test_forward_refs_global_scope():
    """Global scope attrs class with forward references that we can handle automatically."""
    # Class is defined in the global scope
    fields = {fi.name: fi for fi in get_fields_from_attrs_class(GlobalWithFwdRefs)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    # Resolved by attrs.resolve_types() in get_fields_from_attrs_class
    assert fields["imported_ref"].type_name == "Party"
    assert fields["imported_ref"].raw_type == attrs_examples.Party
    assert fields["nested_imported_ref"].type_name == "Optional[Quest]"
    assert fields["nested_imported_ref"].raw_type == Optional[attrs_examples.Quest]
    assert fields["self_ref"].type_name == "GlobalWithFwdRefs"
    assert fields["self_ref"].raw_type == GlobalWithFwdRefs
    assert fields["nested_self_ref"].type_name == "Optional[GlobalWithFwdRefs]"
    assert fields["nested_self_ref"].raw_type == Optional[GlobalWithFwdRefs]
    assert fields["global_ref_before"].type_name == "GlobalOtherClassBefore"
    assert fields["global_ref_before"].raw_type == GlobalOtherClassBefore
    assert fields["nested_global_ref_before"].type_name == "Optional[GlobalOtherClassBefore]"
    assert fields["nested_global_ref_before"].raw_type == Optional[GlobalOtherClassBefore]
    assert fields["global_ref_after"].type_name == "GlobalOtherClassAfter"
    assert fields["global_ref_after"].raw_type == GlobalOtherClassAfter
    assert fields["nested_global_ref_after"].type_name == "Optional[GlobalOtherClassAfter]"
    assert fields["nested_global_ref_after"].raw_type == Optional[GlobalOtherClassAfter]

    # Can add to diagram without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(GlobalWithFwdRefs)


def test_forward_refs_fn_scope_auto_resolvable():
    """Function scope attrs class with forward references that we can automatically resolve."""

    # Resolved by attrs.resolve_types() in get_fields_from_attrs_class
    @define
    class FnScopeAutomaticallyResolvable:
        imported_ref: "attrs_examples.Party"
        nested_imported_ref: Optional["attrs_examples.Quest"]
        global_ref: "GlobalOtherClassBefore"
        nested_global_ref: Optional["GlobalOtherClassBefore"]

    fields = {fi.name: fi for fi in get_fields_from_attrs_class(FnScopeAutomaticallyResolvable)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    assert fields["imported_ref"].type_name == "Party"
    assert fields["imported_ref"].raw_type == attrs_examples.Party
    assert fields["nested_imported_ref"].type_name == "Optional[Quest]"
    assert fields["nested_imported_ref"].raw_type == Optional[attrs_examples.Quest]
    assert fields["global_ref"].type_name == "GlobalOtherClassBefore"
    assert fields["global_ref"].raw_type == GlobalOtherClassBefore
    assert fields["nested_global_ref"].type_name == "Optional[GlobalOtherClassBefore]"
    assert fields["nested_global_ref"].raw_type == Optional[GlobalOtherClassBefore]

    # Can add to diagram without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(FnScopeAutomaticallyResolvable)


def test_forward_refs_fn_scope_manual_resolvable():
    """Function scope model with forward references that we need to manually resolve."""

    @define
    class FnScopeOtherClassBefore:
        """Another class to be referenced as a forward reference. Defined before the class that
        references it."""

        my_field: str

    @define
    class FnScopeManuallyResolvable:
        self_ref: "FnScopeManuallyResolvable"
        nested_self_ref: Optional["FnScopeManuallyResolvable"]
        sibling_ref_before: "FnScopeOtherClassBefore"
        nested_sibling_ref_before: "Optional[FnScopeOtherClassBefore]"
        sibling_ref_after: "FnScopeOtherClassAfter"
        nested_sibling_ref_after: Optional["FnScopeOtherClassAfter"]

    @define
    class FnScopeOtherClassAfter:
        """Another class to be referenced as a forward reference. Defined after the class that
        references it."""

        my_field: str

    with pytest.raises(UnresolvableForwardRefError, match="'FnScopeManuallyResolvable'"):
        diagram = EntityRelationshipDiagram()
        diagram.add_model(FnScopeManuallyResolvable)

    with pytest.raises(UnresolvableForwardRefError, match="'FnScopeManuallyResolvable'"):
        get_fields_from_attrs_class(FnScopeManuallyResolvable)

    # Call attrs.resolve_types() to manually resolve
    resolve_types(FnScopeManuallyResolvable, localns=locals())

    # Adding to diagram should now work without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(FnScopeManuallyResolvable)

    # Fields should match expected
    fields = {fi.name: fi for fi in get_fields_from_attrs_class(FnScopeManuallyResolvable)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    assert fields["self_ref"].type_name == "FnScopeManuallyResolvable"
    assert fields["self_ref"].raw_type == FnScopeManuallyResolvable
    assert fields["nested_self_ref"].type_name == "Optional[FnScopeManuallyResolvable]"
    assert fields["nested_self_ref"].raw_type == Optional[FnScopeManuallyResolvable]
    assert fields["sibling_ref_before"].type_name == "FnScopeOtherClassBefore"
    assert fields["sibling_ref_before"].raw_type == FnScopeOtherClassBefore
    assert fields["nested_sibling_ref_before"].type_name == "Optional[FnScopeOtherClassBefore]"
    assert fields["nested_sibling_ref_before"].raw_type == Optional[FnScopeOtherClassBefore]
    assert fields["sibling_ref_after"].type_name == "FnScopeOtherClassAfter"
    assert fields["sibling_ref_after"].raw_type == FnScopeOtherClassAfter
    assert fields["nested_sibling_ref_after"].type_name == "Optional[FnScopeOtherClassAfter]"
    assert fields["nested_sibling_ref_after"].raw_type == Optional[FnScopeOtherClassAfter]
