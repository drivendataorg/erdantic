from pprint import pprint
from typing import Optional

import msgspec
import pytest

from erdantic.core import EntityRelationshipDiagram, FullyQualifiedName
import erdantic.examples.msgspec as msgspec_examples
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins.msgspec import (
    get_fields_from_msgspec_struct,
    is_msgspec_struct,
)


def test_is_msgspec_struct():
    class NotAStruct:
        pass

    assert is_msgspec_struct(msgspec_examples.Party)
    assert is_msgspec_struct(msgspec_examples.QuestGiver)
    assert not is_msgspec_struct(
        msgspec_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_msgspec_struct("Hello")
    assert not is_msgspec_struct(str)
    assert not is_msgspec_struct(NotAStruct)


def test_get_fields_from_msgspec_struct():
    fields = get_fields_from_msgspec_struct(msgspec_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(msgspec_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(msgspec_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(msgspec_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "list[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(msgspec_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"


class GlobalOtherClassBefore(msgspec.Struct):
    """Another struct to be referenced as a forward reference. Defined before the struct that
    references it."""

    my_field: str


class GlobalWithFwdRefs(msgspec.Struct):
    """Globally defined struct with forward references. This should have no problems being
    automatically resolved."""

    # Resolved by resolve_types_on_dataclass in get_fields_from_msgspec_struct
    imported_ref: "msgspec_examples.Party"
    nested_imported_ref: Optional["msgspec_examples.Quest"]
    self_ref: "GlobalWithFwdRefs"
    nested_self_ref: Optional["GlobalWithFwdRefs"]
    global_ref_before: "GlobalOtherClassBefore"
    nested_global_ref_before: Optional["GlobalOtherClassBefore"]
    global_ref_after: "GlobalOtherClassAfter"
    nested_global_ref_after: Optional["GlobalOtherClassAfter"]


class GlobalOtherClassAfter(msgspec.Struct):
    """Another struct to be referenced as a forward reference. Defined after the struct that
    references it."""

    my_field: str


def test_forward_refs_global_scope():
    """Global scope struct with forward references that we can handle automatically."""
    # Class is defined in the global scope
    fields = {fi.name: fi for fi in get_fields_from_msgspec_struct(GlobalWithFwdRefs)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    # Resolved by resolve_types_on_dataclass in get_fields_from_msgspec_struct
    assert fields["imported_ref"].type_name == "Party"
    assert fields["imported_ref"].raw_type == msgspec_examples.Party
    assert fields["nested_imported_ref"].type_name == "Optional[Quest]"
    assert fields["nested_imported_ref"].raw_type == Optional[msgspec_examples.Quest]
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
    """Function scope struct with forward references that we can automatically resolve."""

    # Resolved by resolve_types_on_dataclass in get_fields_from_msgspec_struct
    class FnScopeAutomaticallyResolvable(msgspec.Struct):
        imported_ref: "msgspec_examples.Party"
        nested_imported_ref: Optional["msgspec_examples.Quest"]
        global_ref: "GlobalOtherClassBefore"
        nested_global_ref: Optional["GlobalOtherClassBefore"]

    fields = {fi.name: fi for fi in get_fields_from_msgspec_struct(FnScopeAutomaticallyResolvable)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    assert fields["imported_ref"].type_name == "Party"
    assert fields["imported_ref"].raw_type == msgspec_examples.Party
    assert fields["nested_imported_ref"].type_name == "Optional[Quest]"
    assert fields["nested_imported_ref"].raw_type == Optional[msgspec_examples.Quest]
    assert fields["global_ref"].type_name == "GlobalOtherClassBefore"
    assert fields["global_ref"].raw_type == GlobalOtherClassBefore
    assert fields["nested_global_ref"].type_name == "Optional[GlobalOtherClassBefore]"
    assert fields["nested_global_ref"].raw_type == Optional[GlobalOtherClassBefore]

    # Can add to diagram without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(FnScopeAutomaticallyResolvable)


def test_forward_refs_fn_scope_manual_resolvable():
    """Function scope model with forward references that we need to manually resolve."""

    class FnScopeOtherClassBefore(msgspec.Struct):
        """Another class to be referenced as a forward reference. Defined before the class that
        references it."""

        my_field: str

    class FnScopeManuallyResolvable(msgspec.Struct):
        self_ref: "FnScopeManuallyResolvable"
        nested_self_ref: Optional["FnScopeManuallyResolvable"]
        sibling_ref_before: "FnScopeOtherClassBefore"
        nested_sibling_ref_before: "Optional[FnScopeOtherClassBefore]"
        sibling_ref_after: "FnScopeOtherClassAfter"
        nested_sibling_ref_after: Optional["FnScopeOtherClassAfter"]

    class FnScopeOtherClassAfter(msgspec.Struct):
        """Another class to be referenced as a forward reference. Defined after the class that
        references it."""

        my_field: str

    with pytest.raises(UnresolvableForwardRefError, match="'FnScopeManuallyResolvable'"):
        diagram = EntityRelationshipDiagram()
        diagram.add_model(FnScopeManuallyResolvable)

    with pytest.raises(UnresolvableForwardRefError, match="'FnScopeManuallyResolvable'"):
        get_fields_from_msgspec_struct(FnScopeManuallyResolvable)

    # Don't currently support manually resolving forward references for structs

    # Call attrs.resolve_types() to manually resolve
    # resolve_types_on_struct(FnScopeManuallyResolvable, localns=locals())

    # Adding to diagram should now work without error
    # diagram = EntityRelationshipDiagram()
    # diagram.add_model(FnScopeManuallyResolvable)

    # Fields should match expected
    # fields = {fi.name: fi for fi in get_fields_from_msgspec_struct(FnScopeManuallyResolvable)}
    # pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    # assert fields["self_ref"].type_name == "FnScopeManuallyResolvable"
    # assert fields["self_ref"].raw_type == FnScopeManuallyResolvable
    # assert fields["nested_self_ref"].type_name == "Optional[FnScopeManuallyResolvable]"
    # assert fields["nested_self_ref"].raw_type == Optional[FnScopeManuallyResolvable]
    # assert fields["sibling_ref_before"].type_name == "FnScopeOtherClassBefore"
    # assert fields["sibling_ref_before"].raw_type == FnScopeOtherClassBefore
    # assert fields["nested_sibling_ref_before"].type_name == "Optional[FnScopeOtherClassBefore]"
    # assert fields["nested_sibling_ref_before"].raw_type == Optional[FnScopeOtherClassBefore]
    # assert fields["sibling_ref_after"].type_name == "FnScopeOtherClassAfter"
    # assert fields["sibling_ref_after"].raw_type == FnScopeOtherClassAfter
    # assert fields["nested_sibling_ref_after"].type_name == "Optional[FnScopeOtherClassAfter]"
    # assert fields["nested_sibling_ref_after"].raw_type == Optional[FnScopeOtherClassAfter]
