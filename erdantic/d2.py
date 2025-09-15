from __future__ import annotations

from textwrap import dedent, indent

from erdantic.core import Cardinality, EntityRelationshipDiagram, Modality


def _escape_quotes(s: str) -> str:
    return s.replace('"', r"\"")


def _quote_identifier(name: str) -> str:
    """Always quote D2 identifiers used as shape keys and connection labels.
    Note: field names inside class bodies are intentionally not quoted to match snapshots."""
    return f'"{_escape_quotes(name)}"'


def _maybe_quote_value(value: str) -> str:
    """Quote values only if they contain special characters (e.g., type annotations)."""
    if any(c in value for c in " -.,;()[]{}<>|"):
        return f'"{_escape_quotes(value)}"'
    return value


def _get_visibility_prefix(name: str) -> str:
    """Determines the UML visibility prefix based on Python's naming conventions."""
    if name.startswith("__") and not name.endswith("__"):
        return "-"  # Private
    elif name.startswith("_") and not name.endswith("_"):
        return "#"  # Protected
    else:
        return "+"  # Public


def _get_crowsfoot_d2(cardinality: Cardinality, modality: Modality) -> str:
    """Map (Cardinality, Modality) to a D2 arrowhead shape token.

    D2 supports crow's-foot tokens: cf-one, cf-one-required, cf-many, cf-many-required.
    For cardinality UNSPECIFIED, we fall back to ONE and use modality to choose required vs not.
    """
    if cardinality == Cardinality.MANY:
        return "cf-many-required" if modality == Modality.ONE else "cf-many"
    if cardinality == Cardinality.ONE:
        return "cf-one-required" if modality == Modality.ONE else "cf-one"
    # UNSPECIFIED cardinality -> treat as ONE by default
    return "cf-one-required" if modality == Modality.ONE else "cf-one"


_REL_DEF_TEMPLATE = dedent(
    """\
    {source_model_name} {connection} {target_model_name}: {label} {{
    {attributes}
    }}
    """
)


def render_d2(diagram: EntityRelationshipDiagram) -> str:
    """Renders an EntityRelationshipDiagram into the D2 class diagram format."""
    d2_parts: list[str] = []

    # Define all class shapes first
    for model in diagram.models.values():
        class_name = _quote_identifier(model.name)
        class_def = [f"{class_name}: {{", "  shape: class"]

        if not model.fields:
            class_def.append("  # This class has no fields to display in the diagram.")
        else:
            for field in model.fields.values():
                field_type = _maybe_quote_value(field.type_name)
                visibility = _get_visibility_prefix(field.name)
                class_def.append(f"  {visibility}{field.name}: {field_type}")

        class_def.append("}\n")
        d2_parts.append("\n".join(class_def))

    # Define all relationships between classes
    for edge in diagram.edges.values():
        source_model = diagram.models.get(str(edge.source_model_full_name))
        target_model = diagram.models.get(str(edge.target_model_full_name))
        if not source_model or not target_model:
            continue

        source_model_name = _quote_identifier(source_model.name)
        target_model_name = _quote_identifier(target_model.name)
        label = _quote_identifier(edge.source_field_name)

        connection = "->"  # Directed from source to target

        target_shape = _get_crowsfoot_d2(edge.target_cardinality, edge.target_modality)
        attributes = [f"target-arrowhead.shape: {target_shape}"]

        # Source side: omit entirely when both are UNSPECIFIED. Otherwise, map and include.
        if not (
            edge.source_cardinality == Cardinality.UNSPECIFIED
            and edge.source_modality == Modality.UNSPECIFIED
        ):
            source_shape = _get_crowsfoot_d2(edge.source_cardinality, edge.source_modality)
            attributes.append(f"source-arrowhead.shape: {source_shape}")
            connection = "<->"  # Bidirectional if source side is specified

        d2_parts.append(
            _REL_DEF_TEMPLATE.format(
                source_model_name=source_model_name,
                connection=connection,
                target_model_name=target_model_name,
                label=label,
                attributes=indent("\n".join(attributes), " " * 2),
            )
        )

    return "\n".join(d2_parts)
