from __future__ import annotations

import re

from erdantic.core import Cardinality, EntityRelationshipDiagram, Modality


_CARDINALITY_MARKERS = {
    (Cardinality.ONE, Modality.ONE): "||",
    (Cardinality.ONE, Modality.ZERO): "o|",
    (Cardinality.MANY, Modality.ONE): "|{",
    (Cardinality.MANY, Modality.ZERO): "o{",
}


def _identifier(name: str) -> str:
    """Return a Mermaid-safe identifier while preserving ordinary Python names."""
    identifier = re.sub(r"[^A-Za-z0-9_]", "_", name)
    return identifier or "unnamed"


def _attribute_type(type_name: str) -> str:
    """Keep type annotations readable while limiting them to Mermaid type characters."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", type_name)


def _target_marker(cardinality: Cardinality, modality: Modality) -> str:
    if cardinality == Cardinality.UNSPECIFIED:
        cardinality = Cardinality.ONE
    if modality == Modality.UNSPECIFIED:
        modality = Modality.ZERO
    return _CARDINALITY_MARKERS[(cardinality, modality)]


def render_mermaid(diagram: EntityRelationshipDiagram) -> str:
    """Render an EntityRelationshipDiagram as a Mermaid ER diagram."""
    lines = ["erDiagram"]

    for model in diagram.models.values():
        lines.append(f"    {_identifier(model.name)} {{")
        for field in model.fields.values():
            lines.append(
                f"        {_attribute_type(field.type_name)} {_identifier(field.name)}"
            )
        lines.append("    }")

    for edge in diagram.edges.values():
        source = _identifier(edge.source_model_full_name.qual_name.split(".")[-1])
        target = _identifier(edge.target_model_full_name.qual_name.split(".")[-1])
        target_marker = _target_marker(edge.target_cardinality, edge.target_modality)
        lines.append(f"    {source} ||--{target_marker} {target} : {edge.source_field_name}")

    return "\n".join(lines) + "\n"
