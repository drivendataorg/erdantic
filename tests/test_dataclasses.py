import dataclasses
from dataclasses import dataclass
from pprint import pprint
import sys
from typing import Optional

if sys.version_info >= (3, 9):
    from typing import Annotated, get_type_hints
else:
    from typing_extensions import Annotated, get_type_hints

import pytest

from erdantic.core import EntityRelationshipDiagram, FullyQualifiedName
import erdantic.examples.dataclasses as dataclasses_examples
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins.dataclasses import (
    get_fields_from_dataclass,
    is_dataclass_class,
    resolve_types_on_dataclass,
)


def test_is_dataclass():
    class NotADataclass:
        pass

    assert is_dataclass_class(dataclasses_examples.Party)
    assert is_dataclass_class(dataclasses_examples.QuestGiver)
    assert not is_dataclass_class(
        dataclasses_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_dataclass_class("Hello")
    assert not is_dataclass_class(str)
    assert not is_dataclass_class(NotADataclass)


def test_get_fields_from_dataclass():
    fields = get_fields_from_dataclass(dataclasses_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(dataclasses_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(dataclasses_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(dataclasses_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "List[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(dataclasses_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"


@dataclass
class GlobalOtherClassBefore:
    """Another dataclass to be referenced as a forward reference. Defined before the class that
    references it."""

    my_field: str


@dataclass
class GlobalWithFwdRefs:
    """Globally defined dataclass with forward references. This should have no problems being
    automatically resolved."""

    # Resolved by resolve_types_on_dataclass in get_fields_from_dataclass
    imported_ref: "dataclasses_examples.Party"
    nested_imported_ref: Optional["dataclasses_examples.Quest"]
    self_ref: "GlobalWithFwdRefs"
    nested_self_ref: Optional["GlobalWithFwdRefs"]
    global_ref_before: "GlobalOtherClassBefore"
    nested_global_ref_before: Optional["GlobalOtherClassBefore"]
    global_ref_after: "GlobalOtherClassAfter"
    nested_global_ref_after: Optional["GlobalOtherClassAfter"]


@dataclass
class GlobalOtherClassAfter:
    """Another dataclass to be referenced as a forward reference. Defined after the class that
    references it."""

    my_field: str


def test_forward_refs_global_scope():
    """Global scope dataclass with forward references that we can handle automatically."""
    # Class is defined in the global scope
    fields = {fi.name: fi for fi in get_fields_from_dataclass(GlobalWithFwdRefs)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    # Resolved by resolve_types_on_dataclass in get_fields_from_dataclass
    assert fields["imported_ref"].type_name == "Party"
    assert fields["imported_ref"].raw_type == dataclasses_examples.Party
    assert fields["nested_imported_ref"].type_name == "Optional[Quest]"
    assert fields["nested_imported_ref"].raw_type == Optional[dataclasses_examples.Quest]
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
    """Function scope dataclass with forward references that we can automatically resolve."""

    # Resolved by resolve_types_on_dataclass in get_fields_from_dataclass
    @dataclass
    class FnScopeAutomaticallyResolvable:
        imported_ref: "dataclasses_examples.Party"
        nested_imported_ref: Optional["dataclasses_examples.Quest"]
        global_ref: "GlobalOtherClassBefore"
        nested_global_ref: Optional["GlobalOtherClassBefore"]

    fields = {fi.name: fi for fi in get_fields_from_dataclass(FnScopeAutomaticallyResolvable)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    assert fields["imported_ref"].type_name == "Party"
    assert fields["imported_ref"].raw_type == dataclasses_examples.Party
    assert fields["nested_imported_ref"].type_name == "Optional[Quest]"
    assert fields["nested_imported_ref"].raw_type == Optional[dataclasses_examples.Quest]
    assert fields["global_ref"].type_name == "GlobalOtherClassBefore"
    assert fields["global_ref"].raw_type == GlobalOtherClassBefore
    assert fields["nested_global_ref"].type_name == "Optional[GlobalOtherClassBefore]"
    assert fields["nested_global_ref"].raw_type == Optional[GlobalOtherClassBefore]

    # Can add to diagram without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(FnScopeAutomaticallyResolvable)


def test_forward_refs_fn_scope_manual_resolvable():
    """Function scope model with forward references that we need to manually resolve."""

    @dataclass
    class FnScopeOtherClassBefore:
        """Another class to be referenced as a forward reference. Defined before the class that
        references it."""

        my_field: str

    @dataclass
    class FnScopeManuallyResolvable:
        self_ref: "FnScopeManuallyResolvable"
        nested_self_ref: Optional["FnScopeManuallyResolvable"]
        sibling_ref_before: "FnScopeOtherClassBefore"
        nested_sibling_ref_before: "Optional[FnScopeOtherClassBefore]"
        sibling_ref_after: "FnScopeOtherClassAfter"
        nested_sibling_ref_after: Optional["FnScopeOtherClassAfter"]

    @dataclass
    class FnScopeOtherClassAfter:
        """Another class to be referenced as a forward reference. Defined after the class that
        references it."""

        my_field: str

    with pytest.raises(UnresolvableForwardRefError, match="'FnScopeManuallyResolvable'"):
        diagram = EntityRelationshipDiagram()
        diagram.add_model(FnScopeManuallyResolvable)

    with pytest.raises(UnresolvableForwardRefError, match="'FnScopeManuallyResolvable'"):
        get_fields_from_dataclass(FnScopeManuallyResolvable)

    # Call attrs.resolve_types() to manually resolve
    resolve_types_on_dataclass(FnScopeManuallyResolvable, localns=locals())

    # Adding to diagram should now work without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(FnScopeManuallyResolvable)

    # Fields should match expected
    fields = {fi.name: fi for fi in get_fields_from_dataclass(FnScopeManuallyResolvable)}
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


@dataclass
class ModelWithAnnotated:
    annotated_field: Annotated[str, "My annotation"]


def test_annotated():
    """resolve_types_on_dataclass in the field extractor should not clobber Annotated type hints
    in fields, but the rendered type name should be the inner type without extra metadata.
    """
    field_infos = get_fields_from_dataclass(ModelWithAnnotated)
    print(field_infos)
    assert len(field_infos) == 1
    assert field_infos[0].raw_type == Annotated[str, "My annotation"]
    assert field_infos[0].type_name == "str"

    fields = dataclasses.fields(ModelWithAnnotated)
    print(fields)
    assert len(fields) == 1
    assert fields[0].type == Annotated[str, "My annotation"]

    type_hints = get_type_hints(ModelWithAnnotated, include_extras=True)
    print(type_hints)
    assert len(type_hints) == 1
    assert type_hints["annotated_field"] == Annotated[str, "My annotation"]
