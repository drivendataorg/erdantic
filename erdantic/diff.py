from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from erdantic.core import Cardinality, EntityRelationshipDiagram, Modality


@dataclass(frozen=True)
class SchemaChange:
    kind: str
    model: str
    field: str | None = None
    before: str | None = None
    after: str | None = None
    breaking: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "model": self.model,
            "field": self.field,
            "before": self.before,
            "after": self.after,
            "breaking": self.breaking,
        }


def _model_map(diagram: EntityRelationshipDiagram):
    return {model.name: model for model in diagram.models.values()}


def _edge_map(diagram: EntityRelationshipDiagram):
    return {
        (
            diagram.models[str(edge.source_model_full_name)].name,
            edge.source_field_name,
            diagram.models[str(edge.target_model_full_name)].name,
        ): edge
        for edge in diagram.edges.values()
    }


def _field_type(field) -> str:
    return field.type_name


def _is_optional_type(type_name: str) -> bool:
    return "Optional[" in type_name or " | None" in type_name or type_name.endswith("|None")


def _without_optional(type_name: str) -> str:
    return type_name.replace("Optional[", "").replace("]", "").replace(" | None", "")


def _relationship_signature(edge) -> str:
    return (
        f"{edge.target_cardinality.value}/{edge.target_modality.value}"
        f";{edge.source_cardinality.value}/{edge.source_modality.value}"
    )


def _is_breaking_cardinality(before, after) -> bool:
    cardinality_breaking = (
        before.target_cardinality == Cardinality.MANY
        and after.target_cardinality == Cardinality.ONE
    )
    modality_breaking = (
        before.target_modality == Modality.ZERO
        and after.target_modality == Modality.ONE
    )
    return cardinality_breaking or modality_breaking


def compare_diagrams(
    before: EntityRelationshipDiagram, after: EntityRelationshipDiagram
) -> list[SchemaChange]:
    """Compare two diagrams and return deterministic schema changes."""
    changes: list[SchemaChange] = []
    before_models = _model_map(before)
    after_models = _model_map(after)

    for model_name in sorted(set(before_models) - set(after_models)):
        changes.append(SchemaChange("model_removed", model_name, breaking=True))
    for model_name in sorted(set(after_models) - set(before_models)):
        changes.append(SchemaChange("model_added", model_name))

    for model_name in sorted(set(before_models) & set(after_models)):
        before_fields = before_models[model_name].fields
        after_fields = after_models[model_name].fields
        removed = set(before_fields) - set(after_fields)
        added = set(after_fields) - set(before_fields)

        # A one-to-one same-type add/remove is the useful rename signal available
        # from static annotations without requiring explicit migration metadata.
        if len(removed) == len(added) == 1:
            old_name = next(iter(removed))
            new_name = next(iter(added))
            if _field_type(before_fields[old_name]) == _field_type(after_fields[new_name]):
                changes.append(
                    SchemaChange(
                        "field_renamed",
                        model_name,
                        field=old_name,
                        before=old_name,
                        after=new_name,
                        breaking=True,
                    )
                )
                removed.clear()
                added.clear()

        for field_name in sorted(removed):
            changes.append(
                SchemaChange(
                    "field_removed",
                    model_name,
                    field=field_name,
                    before=_field_type(before_fields[field_name]),
                    breaking=True,
                )
            )
        for field_name in sorted(added):
            field_type = _field_type(after_fields[field_name])
            changes.append(
                SchemaChange(
                    "field_added",
                    model_name,
                    field=field_name,
                    after=field_type,
                    breaking="Optional" not in field_type and " | None" not in field_type,
                )
            )
        for field_name in sorted(set(before_fields) & set(after_fields)):
            before_type = _field_type(before_fields[field_name])
            after_type = _field_type(after_fields[field_name])
            if before_type != after_type:
                if (
                    _without_optional(before_type) == after_type
                    and _is_optional_type(before_type)
                ):
                    changes.append(
                        SchemaChange(
                            "field_requiredness_changed",
                            model_name,
                            field=field_name,
                            before=before_type,
                            after=after_type,
                            breaking=True,
                        )
                    )
                    continue
                if (
                    _without_optional(after_type) == before_type
                    and _is_optional_type(after_type)
                ):
                    changes.append(
                        SchemaChange(
                            "field_requiredness_changed",
                            model_name,
                            field=field_name,
                            before=before_type,
                            after=after_type,
                        )
                    )
                    continue
                changes.append(
                    SchemaChange(
                        "field_type_changed",
                        model_name,
                        field=field_name,
                        before=before_type,
                        after=after_type,
                        breaking=True,
                    )
                )

    before_edges = _edge_map(before)
    after_edges = _edge_map(after)
    for key in sorted(set(before_edges) - set(after_edges)):
        source, field, target = key
        changes.append(
            SchemaChange(
                "relationship_removed",
                source,
                field=field,
                before=target,
                breaking=True,
            )
        )
    for key in sorted(set(after_edges) - set(before_edges)):
        source, field, target = key
        changes.append(SchemaChange("relationship_added", source, field=field, after=target))
    for key in sorted(set(before_edges) & set(after_edges)):
        before_edge = before_edges[key]
        after_edge = after_edges[key]
        before_signature = _relationship_signature(before_edge)
        after_signature = _relationship_signature(after_edge)
        if before_signature != after_signature:
            changes.append(
                SchemaChange(
                    "relationship_changed",
                    key[0],
                    field=key[1],
                    before=before_signature,
                    after=after_signature,
                    breaking=_is_breaking_cardinality(before_edge, after_edge),
                )
            )

    return changes


def render_json(changes: list[SchemaChange]) -> str:
    return json.dumps({"changes": [change.to_dict() for change in changes]}, indent=2)


def render_markdown(changes: list[SchemaChange]) -> str:
    if not changes:
        return "No schema changes detected.\n"
    lines = [
        "# Schema Changes",
        "",
        "| Change | Model | Field | Before | After | Breaking |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for change in changes:
        values = [
            change.kind,
            change.model,
            change.field or "",
            change.before or "",
            change.after or "",
            "yes" if change.breaking else "no",
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
    return "\n".join(lines) + "\n"


def render_mermaid(changes: list[SchemaChange]) -> str:
    if not changes:
        return "flowchart LR\n    clean[No schema changes detected]\n"

    before_nodes: list[str] = []
    change_nodes: list[str] = []
    after_nodes: list[str] = []
    connections: list[str] = []
    classes: list[str] = []
    for index, change in enumerate(changes, start=1):
        subject = change.model + (f".{change.field}" if change.field else "")
        before_value = change.before or "not present"
        after_value = change.after or "not present"
        if change.kind == "model_added":
            after_value = "present"
        elif change.kind == "model_removed":
            before_value = "present"
        kind = change.kind.replace("_", " ")
        before_id = f"before{index}"
        change_id = f"change{index}"
        after_id = f"after{index}"
        before_label = _mermaid_label(f"{subject}<br/>{before_value}")
        change_label = _mermaid_label(f"{kind}<br/>{subject}")
        after_label = _mermaid_label(f"{subject}<br/>{after_value}")
        before_nodes.extend(
            [
                f'    {before_id}["{before_label}"]',
            ]
        )
        change_nodes.extend(
            [
                f'    {change_id}["{change_label}"]',
            ]
        )
        after_nodes.extend(
            [
                f'    {after_id}["{after_label}"]',
            ]
        )
        connections.append(f"    {before_id} --> {change_id} --> {after_id}")
        if change.breaking:
            classes.append(f"    class {before_id},{change_id},{after_id} breaking")
        else:
            classes.append(f"    class {before_id},{change_id},{after_id} nonbreaking")
    lines = ["flowchart LR", '    subgraph before["Before"]']
    lines.extend(before_nodes)
    lines.append("    end")
    lines.append('    subgraph changes["Changes"]')
    lines.extend(change_nodes)
    lines.append("    end")
    lines.append('    subgraph after["After"]')
    lines.extend(after_nodes)
    lines.append("    end")
    lines.extend(connections)
    lines.extend(classes)
    lines.extend(
        [
            "    classDef breaking fill:#ffdddd,stroke:#cc0000,color:#000000",
            "    classDef nonbreaking fill:#eef5ff,stroke:#446688,color:#000000",
            "",
        ]
    )
    return "\n".join(lines)


def _mermaid_label(value: str) -> str:
    return value.replace('"', "'").replace("|", "&#124;")
