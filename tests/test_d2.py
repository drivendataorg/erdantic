import erdantic as erd
from erdantic.core import Cardinality, Modality
from erdantic.d2 import (
    _get_crowsfoot_d2,
    _get_visibility_prefix,
    _maybe_quote_value,
    _quote_identifier,
    render_d2,
)
from erdantic.examples import pydantic


def test_render_d2():
    """Test full D2 rendering."""
    diagram = erd.create(pydantic.Party)
    d2_string = render_d2(diagram)

    # Check for class definitions (identifiers are always quoted)
    assert '"Party": {\n  shape: class' in d2_string
    assert '"Adventurer": {\n  shape: class' in d2_string
    assert '"Quest": {\n  shape: class' in d2_string
    assert '"QuestGiver": {\n  shape: class' in d2_string

    # Check for fields
    assert "+name: str" in d2_string
    assert '+active_quest: "Optional[Quest]"' in d2_string

    # Check for relationships and crow's foot
    assert '"Party" -> "Adventurer": "members"' in d2_string
    assert "target-arrowhead.shape: cf-many" in d2_string
    assert '"Party" -> "Quest": "active_quest"' in d2_string
    assert "target-arrowhead.shape: cf-one" in d2_string
    assert '"Quest" -> "QuestGiver": "giver"' in d2_string
    assert "target-arrowhead.shape: cf-one-required" in d2_string


def test_get_visibility_prefix():
    """Test visibility prefix determination."""
    assert _get_visibility_prefix("public_field") == "+"
    assert _get_visibility_prefix("_protected_field") == "#"
    assert _get_visibility_prefix("__private_field") == "-"


def test_identifier_and_value_quoting():
    """Identifiers are always quoted; values only when special."""
    assert _quote_identifier("ValidName") == '"ValidName"'
    assert _quote_identifier("name with space") == '"name with space"'
    assert _maybe_quote_value("str") == "str"
    assert _maybe_quote_value("list[Item]") == '"list[Item]"'
    assert _maybe_quote_value("Foo | None") == '"Foo | None"'


def test_quote_identifier_escapes_double_quotes():
    """Ensure embedded quotes are escaped inside quoted identifiers."""
    assert _quote_identifier('He said "hi"') == '"He said \\"hi\\""'


def test_get_d2_cardinality_unspecified_combinations():
    """Explicitly cover UNSPECIFIED cardinality/modality combos."""

    # UNSPECIFIED cardinality behaves like ONE; required only if Modality.ONE
    assert _get_crowsfoot_d2(Cardinality.UNSPECIFIED, Modality.UNSPECIFIED) == "cf-one"
    assert _get_crowsfoot_d2(Cardinality.UNSPECIFIED, Modality.ZERO) == "cf-one"
    assert _get_crowsfoot_d2(Cardinality.UNSPECIFIED, Modality.ONE) == "cf-one-required"

    # Sanity checks for explicit ONE/MANY remain consistent
    assert _get_crowsfoot_d2(Cardinality.ONE, Modality.ZERO) == "cf-one"
    assert _get_crowsfoot_d2(Cardinality.MANY, Modality.UNSPECIFIED) == "cf-many"
    assert _get_crowsfoot_d2(Cardinality.MANY, Modality.ONE) == "cf-many-required"


def test_render_d2_with_source_markers():
    """When source cardinality/modality are set, a source arrowhead is rendered."""
    diagram = erd.create(pydantic.Party)
    # Pick the Party.members -> Adventurer edge and set source side explicitly
    edge = next(e for e in diagram.edges.values() if e.source_field_name == "members")
    edge.source_cardinality = Cardinality.ONE
    edge.source_modality = Modality.ONE

    out = render_d2(diagram)
    assert '"Party" <-> "Adventurer": "members"' in out
    assert "target-arrowhead.shape: cf-many" in out
    assert "source-arrowhead.shape: cf-one-required" in out
