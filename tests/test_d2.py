import erdantic as erd
from erdantic.examples import pydantic
from erdantic.d2 import _get_d2_cardinality, _sanitize_name, _get_visibility_prefix, render_d2

def test_render_d2():
    """Test full D2 rendering."""
    diagram = erd.create(pydantic.Party)
    d2_string = render_d2(diagram)

    # Check for class definitions
    assert "Party: {\n  shape: class" in d2_string
    assert "Adventurer: {\n  shape: class" in d2_string
    assert "Quest: {\n  shape: class" in d2_string
    assert "QuestGiver: {\n  shape: class" in d2_string

    # Check for fields
    assert "+name: str" in d2_string
    assert "+active_quest: \"Optional[Quest]\"" in d2_string

    # Check for relationships
    assert "Party -> Adventurer: members" in d2_string
    assert 'target-arrowhead: "1..*"' in d2_string
    assert "Party -> Quest: active_quest" in d2_string
    assert 'target-arrowhead: "0..1"' in d2_string
    assert "Quest -> QuestGiver: giver" in d2_string
    assert 'target-arrowhead: "1"' in d2_string


def test_get_visibility_prefix():
    """Test visibility prefix determination."""
    assert _get_visibility_prefix("public_field") == "+"
    assert _get_visibility_prefix("_protected_field") == "#"
    assert _get_visibility_prefix("__private_field") == "-"


def test_sanitize_name():
    """Test D2 name sanitization."""
    assert _sanitize_name("ValidName") == "ValidName"
    assert _sanitize_name("name with space") == "\"name with space\""
    assert _sanitize_name("list[Item]") == "\"list[Item]\""
