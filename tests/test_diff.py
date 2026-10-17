import json

import erdantic as erd
from erdantic.core import Cardinality, FieldInfo, Modality
from erdantic.diff import compare_diagrams, render_json, render_markdown, render_mermaid
from erdantic.examples import pydantic


def test_compare_field_changes():
    before = erd.create(pydantic.Party)
    after = before.model_copy(deep=True)
    party = after.models["erdantic.examples.pydantic.Party"]

    del party.fields["name"]
    party.fields["new_required"] = FieldInfo(
        model_full_name=party.full_name,
        name="new_required",
        type_name="int",
    )
    party.fields["formed_datetime"].type_name = "str"

    changes = compare_diagrams(before, after)
    kinds = {change.kind for change in changes}
    assert "field_removed" in kinds
    assert "field_added" in kinds
    assert "field_type_changed" in kinds
    assert all(change.breaking for change in changes if change.kind != "field_added")


def test_compare_field_rename():
    before = erd.create(pydantic.Party)
    after = before.model_copy(deep=True)
    party = after.models["erdantic.examples.pydantic.Party"]
    field = party.fields.pop("name")
    field.name = "display_name"
    party.fields["display_name"] = field

    changes = compare_diagrams(before, after)
    assert [change.kind for change in changes] == ["field_renamed"]
    assert changes[0].before == "name"
    assert changes[0].after == "display_name"


def test_compare_relationship_change():
    before = erd.create(pydantic.Party)
    after = before.model_copy(deep=True)
    edge = next(edge for edge in after.edges.values() if edge.source_field_name == "members")
    edge.target_cardinality = Cardinality.ONE
    edge.target_modality = Modality.ONE

    changes = compare_diagrams(before, after)
    relationship = next(change for change in changes if change.kind == "relationship_changed")
    assert relationship.breaking


def test_compare_requiredness_change():
    before = erd.create(pydantic.Party)
    after = before.model_copy(deep=True)
    field = after.models["erdantic.examples.pydantic.Party"].fields["name"]
    field.type_name = "Optional[str]"

    changes = compare_diagrams(before, after)
    requiredness = next(
        change for change in changes if change.kind == "field_requiredness_changed"
    )
    assert not requiredness.breaking


def test_renderers():
    changes = [
        erd.diff.SchemaChange(
            "field_type_changed",
            "Party",
            field="name",
            before="str",
            after="int",
            breaking=True,
        )
    ]
    output = json.loads(render_json(changes))
    assert output["changes"][0]["breaking"] is True
    assert "| field_type_changed | Party | name | str | int | yes |" in render_markdown(changes)
    mermaid = render_mermaid(changes)
    assert 'subgraph before["Before"]' in mermaid
    assert 'subgraph after["After"]' in mermaid
    assert 'before1["Party.name<br/>str"]' in mermaid
    assert 'change1["field type changed<br/>Party.name"]' in mermaid
    assert 'after1["Party.name<br/>int"]' in mermaid
    assert "before1 --> change1 --> after1" in mermaid
    assert "class before1,change1,after1 breaking" in mermaid
