# erdantic/d2.py

from erdantic.core import Cardinality, Edge, EntityRelationshipDiagram, Modality


def _get_d2_cardinality(edge: Edge) -> str:
    """Maps erdantic's cardinality and modality to D2 cardinality strings."""
    is_many = edge.target_cardinality == Cardinality.MANY
    is_nullable = edge.target_modality == Modality.ZERO

    if is_many and is_nullable:
        return '"*"'  # Zero or more
    elif is_many and not is_nullable:
        return '"1..*"'  # One or more
    elif not is_many and is_nullable:
        return '"0..1"'  # Zero or one
    else:  # not is_many and not is_nullable
        return '"1"'  # Exactly one


def _sanitize_name(name: str) -> str:
    """Sanitizes a name for D2 syntax, quoting if it contains special characters."""
    if any(c in name for c in " -.,;()[]{}<>"):
        return f'"{name}"'
    return name


def _get_visibility_prefix(name: str) -> str:
    """Determines the UML visibility prefix based on Python's naming conventions."""
    if name.startswith("__") and not name.endswith("__"):
        return "-"  # Private
    elif name.startswith("_") and not name.endswith("_"):
        return "#"  # Protected
    else:
        return "+"  # Public


def render_d2(diagram: EntityRelationshipDiagram) -> str:
    """Renders an EntityRelationshipDiagram into the D2 class diagram format."""
    d2_parts = []

    # Define all class shapes first
    for model in diagram.models.values():
        class_name = _sanitize_name(model.name)
        class_def = [f"{class_name}: {{", "  shape: class"]

        if not model.fields:
            class_def.append("  # This class has no fields to display in the diagram.")
        else:
            for field in model.fields.values():
                field_type_sanitized = _sanitize_name(field.type_name)
                visibility = _get_visibility_prefix(field.name)
                # Strip leading underscores from the name for a cleaner look in the diagram
                field_name_clean = field.name.lstrip("_")
                field_name_sanitized = _sanitize_name(field_name_clean)
                class_def.append(f"  {visibility}{field_name_sanitized}: {field_type_sanitized}")

        class_def.append("}\n")
        d2_parts.append("\n".join(class_def))

    # Define all relationships between classes
    for edge in diagram.edges.values():
        source_model = diagram.models.get(str(edge.source_model_full_name))
        target_model = diagram.models.get(str(edge.target_model_full_name))

        if not source_model or not target_model:
            continue

        source_model_name = _sanitize_name(source_model.name)
        target_model_name = _sanitize_name(target_model.name)

        label = _sanitize_name(edge.source_field_name)

        # Use a directed arrow for composition/aggregation
        rel_def_line = f"{source_model_name} -> {target_model_name}: {label}"

        d2_cardinality = _get_d2_cardinality(edge)

        # Define the relationship with target cardinality
        rel_def = [f"{rel_def_line} {{", f"  target-arrowhead: {d2_cardinality}", "}\n"]
        d2_parts.append("\n".join(rel_def))

    return "\n".join(d2_parts)
