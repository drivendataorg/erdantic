import erdantic as erd
from erdantic.core import Cardinality, Modality
from erdantic.examples import pydantic
from erdantic.mermaid import _target_marker, render_mermaid


def test_render_mermaid():
    diagram = erd.create(pydantic.Party)
    output = render_mermaid(diagram)

    assert output.startswith("erDiagram\n")
    assert "    Party {" in output
    assert "        list_Adventurer_ members" in output
    assert "        Optional_Quest_ active_quest" in output
    assert "    Party ||--o{ Adventurer : members" in output
    assert "    Party ||--o| Quest : active_quest" in output
    assert "    Quest ||--|| QuestGiver : giver" in output


def test_target_marker():
    assert _target_marker(Cardinality.ONE, Modality.ONE) == "||"
    assert _target_marker(Cardinality.ONE, Modality.ZERO) == "o|"
    assert _target_marker(Cardinality.MANY, Modality.ONE) == "|{"
    assert _target_marker(Cardinality.MANY, Modality.ZERO) == "o{"
    assert _target_marker(Cardinality.UNSPECIFIED, Modality.UNSPECIFIED) == "o|"


def test_mermaid_names_are_sanitized():
    diagram = erd.create(pydantic.Party)
    model = next(iter(diagram.models.values()))
    model.name = "Party With Spaces"
    output = render_mermaid(diagram)
    assert "    Party_With_Spaces {" in output
