from dataclasses import dataclass
from typing import Optional

import pytest

from erdantic.core import FullyQualifiedName
import erdantic.examples.dataclasses as dataclasses_examples
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins.dataclasses import (
    get_fields_from_dataclass,
    is_dataclass_type,
)


def test_is_dataclass():
    class NotADataclass:
        pass

    assert is_dataclass_type(dataclasses_examples.Party)
    assert is_dataclass_type(dataclasses_examples.QuestGiver)
    assert not is_dataclass_type(
        dataclasses_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_dataclass_type("Hello")
    assert not is_dataclass_type(str)
    assert not is_dataclass_type(NotADataclass)


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
class HasForwardRefs:
    fwd_ref: "dataclasses_examples.Party"
    nested_fwd_ref: Optional["dataclasses_examples.Quest"]
    self_fwd_ref: "HasForwardRefs"
    nested_self_fwd_ref: Optional["HasForwardRefs"]


def test_forward_refs():
    # Class is defined in the global scope
    fields = {fi.name: fi for fi in get_fields_from_dataclass(HasForwardRefs)}
    print(fields)
    assert fields["fwd_ref"].type_name == "Party"
    assert fields["fwd_ref"].raw_type == dataclasses_examples.Party
    assert fields["nested_fwd_ref"].type_name == "Optional[Quest]"
    assert fields["nested_fwd_ref"].raw_type == Optional[dataclasses_examples.Quest]
    assert fields["self_fwd_ref"].type_name == "HasForwardRefs"
    assert fields["self_fwd_ref"].raw_type == HasForwardRefs
    assert fields["nested_self_fwd_ref"].type_name == "Optional[HasForwardRefs]"
    assert fields["nested_self_fwd_ref"].raw_type == Optional[HasForwardRefs]

    # Class is defined in a function scope
    @dataclass
    class FnScopeHasForwardRefs:
        fwd_ref: "dataclasses_examples.Party"
        nested_fwd_ref: Optional["dataclasses_examples.Quest"]
        global_fwd_ref: "HasForwardRefs"
        nested_global_fwd_ref: Optional["HasForwardRefs"]

    fields = {fi.name: fi for fi in get_fields_from_dataclass(FnScopeHasForwardRefs)}
    print(fields)
    assert fields["fwd_ref"].type_name == "Party"
    assert fields["fwd_ref"].raw_type == dataclasses_examples.Party
    assert fields["nested_fwd_ref"].type_name == "Optional[Quest]"
    assert fields["nested_fwd_ref"].raw_type == Optional[dataclasses_examples.Quest]
    assert fields["global_fwd_ref"].type_name == "HasForwardRefs"
    assert fields["global_fwd_ref"].raw_type == HasForwardRefs
    assert fields["nested_global_fwd_ref"].type_name == "Optional[HasForwardRefs]"
    assert fields["nested_global_fwd_ref"].raw_type == Optional[HasForwardRefs]


def test_forward_ref_of_local_class():
    @dataclass
    class HasForwardRefsOfLocalClass:
        fwd_ref_of_local: "HasForwardRefsOfLocalClass"

    with pytest.raises(UnresolvableForwardRefError):
        _ = {fi.name: fi for fi in get_fields_from_dataclass(HasForwardRefsOfLocalClass)}
