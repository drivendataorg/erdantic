from __future__ import annotations

from erdantic.core import Cardinality, Edge, EntityRelationshipDiagram, Modality


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


def _get_d2_cardinality(edge: Edge) -> str:
    """Map (Cardinality, Modality) to D2 crow's-foot arrowheads (no quotes)."""
    c = edge.target_cardinality
    m = edge.target_modality

    # MANY
    if c == Cardinality.MANY:
        # Only four arrowheads exist for crow's foot; map unspecified to non-required
        return "cf-many-required" if m == Modality.ONE else "cf-many"

    # ONE
    if c == Cardinality.ONE:
        return "cf-one-required" if m == Modality.ONE else "cf-one"

    # UNSPECIFIED cardinality -> treat as ONE by default
    return "cf-one-required" if m == Modality.ONE else "cf-one"


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
                # Strip leading underscores from the name for a cleaner look in the diagram
                field_name_clean = field.name.lstrip("_")
                field_name = field_name_clean
                class_def.append(f"  {visibility}{field_name}: {field_type}")

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

        rel_def_line = f"{source_model_name} -> {target_model_name}: {label}"
        d2_cardinality = _get_d2_cardinality(edge)

        # Use D2 crow's-foot token without quotes
        rel_def = [f"{rel_def_line} {{", f"  target-arrowhead.shape: {d2_cardinality}", "}\n"]
        d2_parts.append("\n".join(rel_def))

    return "\n".join(d2_parts)
