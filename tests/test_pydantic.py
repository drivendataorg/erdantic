from typing import Optional

import pydantic
import pydantic.v1
import pytest

from erdantic.core import FullyQualifiedName
import erdantic.examples.pydantic as pydantic_examples
import erdantic.examples.pydantic_v1 as pydantic_v1_examples
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins.pydantic import (
    get_fields_from_pydantic_model,
    get_fields_from_pydantic_v1_model,
    is_pydantic_model,
    is_pydantic_v1_model,
)


def test_is_pydantic_model():
    class NotAPydanticModel:
        pass

    assert is_pydantic_model(pydantic_examples.Party)
    assert is_pydantic_model(pydantic_examples.QuestGiver)
    assert not is_pydantic_model(
        pydantic_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_pydantic_model("Hello")
    assert not is_pydantic_model(str)
    assert not is_pydantic_model(NotAPydanticModel)
    assert not is_pydantic_model(pydantic_v1_examples.Party)


def test_get_fields_from_pydantic_model():
    fields = get_fields_from_pydantic_model(pydantic_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(pydantic_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(pydantic_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(pydantic_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "List[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(pydantic_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"


class HasForwardRefs(pydantic.BaseModel):
    fwd_ref: "pydantic_examples.Party"
    nested_fwd_ref: Optional["pydantic_examples.Quest"]
    self_fwd_ref: "HasForwardRefs"
    nested_self_fwd_ref: Optional["HasForwardRefs"]


def test_forward_refs():
    # Class is defined in the global scope
    fields = {fi.name: fi for fi in get_fields_from_pydantic_model(HasForwardRefs)}
    print(fields)
    assert fields["fwd_ref"].type_name == "Party"
    assert fields["fwd_ref"].raw_type == pydantic_examples.Party
    assert fields["nested_fwd_ref"].type_name == "Optional[Quest]"
    assert fields["nested_fwd_ref"].raw_type == Optional[pydantic_examples.Quest]
    assert fields["self_fwd_ref"].type_name == "HasForwardRefs"
    assert fields["self_fwd_ref"].raw_type == HasForwardRefs
    assert fields["nested_self_fwd_ref"].type_name == "Optional[HasForwardRefs]"
    assert fields["nested_self_fwd_ref"].raw_type == Optional[HasForwardRefs]

    # Class is defined in a function scope
    class FnScopeHasForwardRefs(pydantic.BaseModel):
        fwd_ref: "pydantic_examples.Party"
        nested_fwd_ref: Optional["pydantic_examples.Quest"]
        global_fwd_ref: "HasForwardRefs"
        nested_global_fwd_ref: Optional["HasForwardRefs"]
        fwd_ref_of_local: "FnScopeHasForwardRefs"
        nested_fwd_ref_of_local: Optional["FnScopeHasForwardRefs"]

    fields = {fi.name: fi for fi in get_fields_from_pydantic_model(FnScopeHasForwardRefs)}
    print(fields)
    assert fields["fwd_ref"].type_name == "Party"
    assert fields["fwd_ref"].raw_type == pydantic_examples.Party
    assert fields["nested_fwd_ref"].type_name == "Optional[Quest]"
    assert fields["nested_fwd_ref"].raw_type == Optional[pydantic_examples.Quest]
    assert fields["global_fwd_ref"].type_name == "HasForwardRefs"
    assert fields["global_fwd_ref"].raw_type == HasForwardRefs
    assert fields["nested_global_fwd_ref"].type_name == "Optional[HasForwardRefs]"
    assert fields["nested_global_fwd_ref"].raw_type == Optional[HasForwardRefs]
    assert fields["fwd_ref_of_local"].type_name == "FnScopeHasForwardRefs"
    assert fields["fwd_ref_of_local"].raw_type == FnScopeHasForwardRefs
    assert fields["nested_fwd_ref_of_local"].type_name == "Optional[FnScopeHasForwardRefs]"
    assert fields["nested_fwd_ref_of_local"].raw_type == Optional[FnScopeHasForwardRefs]


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


class HasForwardRefsV1(pydantic.v1.BaseModel):
    fwd_ref: "pydantic_v1_examples.Party"
    nested_fwd_ref: Optional["pydantic_v1_examples.Quest"]
    self_fwd_ref: "HasForwardRefsV1"
    nested_self_fwd_ref: Optional["HasForwardRefsV1"]


def test_forward_refs_v1():
    # Class is defined in the global scope
    fields = {fi.name: fi for fi in get_fields_from_pydantic_v1_model(HasForwardRefsV1)}
    print(fields)
    assert fields["fwd_ref"].type_name == "Party"
    assert fields["fwd_ref"].raw_type == pydantic_v1_examples.Party
    assert fields["nested_fwd_ref"].type_name == "Optional[Quest]"
    assert fields["nested_fwd_ref"].raw_type == Optional[pydantic_v1_examples.Quest]
    assert fields["self_fwd_ref"].type_name == "HasForwardRefsV1"
    assert fields["self_fwd_ref"].raw_type == HasForwardRefsV1
    assert fields["nested_self_fwd_ref"].type_name == "Optional[HasForwardRefsV1]"
    assert fields["nested_self_fwd_ref"].raw_type == Optional[HasForwardRefsV1]

    # Class is defined in a function scope
    class FnScopeHasForwardRefs(pydantic.v1.BaseModel):
        fwd_ref: "pydantic_v1_examples.Party"
        nested_fwd_ref: Optional["pydantic_v1_examples.Quest"]
        global_fwd_ref: "HasForwardRefsV1"
        nested_global_fwd_ref: Optional["HasForwardRefsV1"]
        fwd_ref_of_local: "FnScopeHasForwardRefs"
        nested_fwd_ref_of_local: Optional["FnScopeHasForwardRefs"]

    fields = {fi.name: fi for fi in get_fields_from_pydantic_v1_model(FnScopeHasForwardRefs)}
    print(fields)
    assert fields["fwd_ref"].type_name == "Party"
    assert fields["fwd_ref"].raw_type == pydantic_v1_examples.Party
    assert fields["nested_fwd_ref"].type_name == "Optional[Quest]"
    assert fields["nested_fwd_ref"].raw_type == Optional[pydantic_v1_examples.Quest]
    assert fields["global_fwd_ref"].type_name == "HasForwardRefsV1"
    assert fields["global_fwd_ref"].raw_type == HasForwardRefsV1
    assert fields["nested_global_fwd_ref"].type_name == "Optional[HasForwardRefsV1]"
    assert fields["nested_global_fwd_ref"].raw_type == Optional[HasForwardRefsV1]
    assert fields["fwd_ref_of_local"].type_name == "FnScopeHasForwardRefs"
    assert fields["fwd_ref_of_local"].raw_type == FnScopeHasForwardRefs
    assert fields["nested_fwd_ref_of_local"].type_name == "Optional[FnScopeHasForwardRefs]"
    assert fields["nested_fwd_ref_of_local"].raw_type == Optional[FnScopeHasForwardRefs]
