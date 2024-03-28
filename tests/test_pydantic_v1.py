from pprint import pprint
from typing import Optional

import pydantic
import pydantic.v1
import pytest

from erdantic.core import EntityRelationshipDiagram, FullyQualifiedName
import erdantic.examples.pydantic as pydantic_examples
import erdantic.examples.pydantic_v1 as pydantic_v1_examples
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins.pydantic import (
    get_fields_from_pydantic_v1_model,
    is_pydantic_v1_model,
)


def test_is_pydantic_v1_model():
    class NotAPydanticModel:
        pass

    assert is_pydantic_v1_model(pydantic_v1_examples.Party)
    assert is_pydantic_v1_model(pydantic_v1_examples.QuestGiver)
    assert not is_pydantic_v1_model(
        pydantic_v1_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_pydantic_v1_model("Hello")
    assert not is_pydantic_v1_model(str)
    assert not is_pydantic_v1_model(NotAPydanticModel)
    assert not is_pydantic_v1_model(pydantic_examples.Party)


def test_get_fields_from_pydantic_v1_model():
    fields = get_fields_from_pydantic_v1_model(pydantic_v1_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(pydantic_v1_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(pydantic_v1_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(pydantic_v1_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "List[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(pydantic_v1_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"


class GlobalOtherModelBefore(pydantic.v1.BaseModel):
    """Another model to be referenced as a forward reference. Defined before the model that
    references it."""

    my_field: str


class GlobalWithFwdRefs(pydantic.v1.BaseModel):
    """Globally defined model with forward references. This should have no problems being
    automatically resolved."""

    # Automatically resolved by Pydantic
    imported_ref: "pydantic_v1_examples.Party"
    nested_imported_ref: Optional["pydantic_v1_examples.Quest"]
    self_ref: "GlobalWithFwdRefs"
    nested_self_ref: Optional["GlobalWithFwdRefs"]
    global_ref_before: "GlobalOtherModelBefore"
    nested_global_ref_before: Optional["GlobalOtherModelBefore"]
    # Resolved by model_rebuild()
    global_ref_after: "GlobalOtherModelAfter"
    nested_global_ref_after: Optional["GlobalOtherModelAfter"]


class GlobalOtherModelAfter(pydantic.v1.BaseModel):
    """Another model to be referenced as a forward reference. Defined after the model that
    references it."""

    my_field: str


def test_forward_refs_global_scope():
    """Global scope model with forward references that we can handle automatically."""
    # Model is defined in the global scope
    fields = {fi.name: fi for fi in get_fields_from_pydantic_v1_model(GlobalWithFwdRefs)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    # Automatically resolved by Pydantic
    assert fields["imported_ref"].type_name == "Party"
    assert fields["imported_ref"].raw_type == pydantic_v1_examples.Party
    assert fields["nested_imported_ref"].type_name == "Optional[Quest]"
    assert fields["nested_imported_ref"].raw_type == Optional[pydantic_v1_examples.Quest]
    assert fields["self_ref"].type_name == "GlobalWithFwdRefs"
    assert fields["self_ref"].raw_type == GlobalWithFwdRefs
    assert fields["nested_self_ref"].type_name == "Optional[GlobalWithFwdRefs]"
    assert fields["nested_self_ref"].raw_type == Optional[GlobalWithFwdRefs]
    assert fields["global_ref_before"].type_name == "GlobalOtherModelBefore"
    assert fields["global_ref_before"].raw_type == GlobalOtherModelBefore
    assert fields["nested_global_ref_before"].type_name == "Optional[GlobalOtherModelBefore]"
    assert fields["nested_global_ref_before"].raw_type == Optional[GlobalOtherModelBefore]
    # Resolved by update_forward_refs()
    assert fields["global_ref_after"].type_name == "GlobalOtherModelAfter"
    assert fields["global_ref_after"].raw_type == GlobalOtherModelAfter
    assert fields["nested_global_ref_after"].type_name == "Optional[GlobalOtherModelAfter]"
    assert fields["nested_global_ref_after"].raw_type == Optional[GlobalOtherModelAfter]

    # Can add to diagram without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(GlobalWithFwdRefs)


def test_forward_refs_fn_scope_auto_resolvable():
    """Function scope model with forward references that we can automatically resolve."""

    # All automatically resolved by Pydantic
    class FnScopeAutomaticallyResolvable(pydantic.v1.BaseModel):
        imported_ref: "pydantic_v1_examples.Party"
        nested_imported_ref: Optional["pydantic_v1_examples.Quest"]
        global_ref: "GlobalOtherModelBefore"
        nested_global_ref: Optional["GlobalOtherModelBefore"]
        self_ref: "FnScopeAutomaticallyResolvable"
        nested_self_ref: Optional["FnScopeAutomaticallyResolvable"]

    fields = {
        fi.name: fi for fi in get_fields_from_pydantic_v1_model(FnScopeAutomaticallyResolvable)
    }
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    assert fields["imported_ref"].type_name == "Party"
    assert fields["imported_ref"].raw_type == pydantic_v1_examples.Party
    assert fields["nested_imported_ref"].type_name == "Optional[Quest]"
    assert fields["nested_imported_ref"].raw_type == Optional[pydantic_v1_examples.Quest]
    assert fields["global_ref"].type_name == "GlobalOtherModelBefore"
    assert fields["global_ref"].raw_type == GlobalOtherModelBefore
    assert fields["nested_global_ref"].type_name == "Optional[GlobalOtherModelBefore]"
    assert fields["nested_global_ref"].raw_type == Optional[GlobalOtherModelBefore]
    assert fields["self_ref"].type_name == "FnScopeAutomaticallyResolvable"
    assert fields["self_ref"].raw_type == FnScopeAutomaticallyResolvable
    assert fields["nested_self_ref"].type_name == "Optional[FnScopeAutomaticallyResolvable]"
    assert fields["nested_self_ref"].raw_type == Optional[FnScopeAutomaticallyResolvable]

    # Can add to diagram without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(FnScopeAutomaticallyResolvable)


def test_forward_refs_fn_scope_manual_resolvable():
    """Function scope model with forward references that we need to manually resolve."""

    class FnScopeOtherModelBefore(pydantic.v1.BaseModel):
        """Another model to be referenced as a forward reference. Defined before the model that
        references it."""

        my_field: str

    class FnScopeManuallyResolvable(pydantic.v1.BaseModel):
        sibling_ref_before: "FnScopeOtherModelBefore"
        nested_sibling_ref_before: "Optional[FnScopeOtherModelBefore]"
        sibling_ref_after: "FnScopeOtherModelAfter"
        nested_sibling_ref_after: Optional["FnScopeOtherModelAfter"]

    class FnScopeOtherModelAfter(pydantic.v1.BaseModel):
        """Another model to be referenced as a forward reference. Defined after the model that
        references it."""

        my_field: str

    with pytest.raises(UnresolvableForwardRefError, match="'FnScopeOtherModelBefore'"):
        diagram = EntityRelationshipDiagram()
        diagram.add_model(FnScopeManuallyResolvable)

    with pytest.raises(UnresolvableForwardRefError, match="'FnScopeOtherModelBefore'"):
        get_fields_from_pydantic_v1_model(FnScopeManuallyResolvable)

    # Call update_forward_refs to manually resolve
    FnScopeManuallyResolvable.update_forward_refs(**locals())

    # Adding to diagram should now work without error
    diagram = EntityRelationshipDiagram()
    diagram.add_model(FnScopeManuallyResolvable)

    # Fields should match expected
    fields = {fi.name: fi for fi in get_fields_from_pydantic_v1_model(FnScopeManuallyResolvable)}
    pprint({name: (fi.type_name, fi.raw_type) for name, fi in fields.items()})
    assert fields["sibling_ref_before"].type_name == "FnScopeOtherModelBefore"
    assert fields["sibling_ref_before"].raw_type == FnScopeOtherModelBefore
    assert fields["nested_sibling_ref_before"].type_name == "Optional[FnScopeOtherModelBefore]"
    assert fields["nested_sibling_ref_before"].raw_type == Optional[FnScopeOtherModelBefore]
    assert fields["sibling_ref_after"].type_name == "FnScopeOtherModelAfter"
    assert fields["sibling_ref_after"].raw_type == FnScopeOtherModelAfter
    assert fields["nested_sibling_ref_after"].type_name == "Optional[FnScopeOtherModelAfter]"
    assert fields["nested_sibling_ref_after"].raw_type == Optional[FnScopeOtherModelAfter]
