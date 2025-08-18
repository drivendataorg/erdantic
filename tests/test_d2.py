import erdantic as erd
from erdantic.examples import pydantic
from erdantic.d2 import (
    _get_d2_cardinality,
    _quote_identifier,
    _maybe_quote_value,
    _get_visibility_prefix,
    render_d2,
)
from erdantic.core import Cardinality, Modality


def test_render_d2():
    """Test full D2 rendering."""
    diagram = erd.create(pydantic.Party)
    d2_string = render_d2(diagram)

    # Check for class definitions (identifiers are always quoted)
    assert "\"Party\": {\n  shape: class" in d2_string
    assert "\"Adventurer\": {\n  shape: class" in d2_string
    assert "\"Quest\": {\n  shape: class" in d2_string
    assert "\"QuestGiver\": {\n  shape: class" in d2_string

    # Check for fields
    assert "+name: str" in d2_string
    assert "+active_quest: \"Optional[Quest]\"" in d2_string

    # Check for relationships and crow's foot
    assert "\"Party\" -> \"Adventurer\": \"members\"" in d2_string
    assert "target-arrowhead: cf-many" in d2_string
    assert "\"Party\" -> \"Quest\": \"active_quest\"" in d2_string
    assert "target-arrowhead: cf-one" in d2_string
    assert "\"Quest\" -> \"QuestGiver\": \"giver\"" in d2_string
    assert "target-arrowhead: cf-one-required" in d2_string


def test_get_visibility_prefix():
    """Test visibility prefix determination."""
    assert _get_visibility_prefix("public_field") == "+"
    assert _get_visibility_prefix("_protected_field") == "#"
    assert _get_visibility_prefix("__private_field") == "-"


def test_identifier_and_value_quoting():
    """Identifiers are always quoted; values only when special."""
    assert _quote_identifier("ValidName") == "\"ValidName\""
    assert _quote_identifier("name with space") == "\"name with space\""
    assert _maybe_quote_value("str") == "str"
    assert _maybe_quote_value("list[Item]") == "\"list[Item]\""
    assert _maybe_quote_value("Foo | None") == "\"Foo | None\""


def test_quote_identifier_escapes_double_quotes():
    """Ensure embedded quotes are escaped inside quoted identifiers."""
    assert _quote_identifier('He said "hi"') == '"He said \\"hi\\""'

def test_get_d2_cardinality_unspecified_combinations():
    """Explicitly cover UNSPECIFIED cardinality/modality combos."""
    # Take any edge and modify the fields
    diagram = erd.create(pydantic.Party)
    edge = next(iter(diagram.edges.values()))
    e = edge.model_copy()

    # UNSPECIFIED cardinality behaves like ONE; required only if Modality.ONE
    e.target_cardinality = Cardinality.UNSPECIFIED
    e.target_modality = Modality.UNSPECIFIED
    assert _get_d2_cardinality(e) == "cf-one"

    e.target_cardinality = Cardinality.UNSPECIFIED
    e.target_modality = Modality.ZERO
    assert _get_d2_cardinality(e) == "cf-one"

    e.target_cardinality = Cardinality.UNSPECIFIED
    e.target_modality = Modality.ONE
    assert _get_d2_cardinality(e) == "cf-one-required"

    # Sanity checks for explicit ONE/MANY remain consistent
    e.target_cardinality = Cardinality.ONE
    e.target_modality = Modality.ZERO
    assert _get_d2_cardinality(e) == "cf-one"

    e.target_cardinality = Cardinality.MANY
    e.target_modality = Modality.UNSPECIFIED
    assert _get_d2_cardinality(e) == "cf-many"

    e.target_cardinality = Cardinality.MANY
    e.target_modality = Modality.ONE
    assert _get_d2_cardinality(e) == "cf-many-required"
