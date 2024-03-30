from html import escape
from typing import Any, Dict, List, Self

import pydantic
import pydantic_core
from typenames import REMOVE_ALL_MODULES, typenames

from erdantic.core import (
    EntityRelationshipDiagram,
    FieldInfo,
    FullyQualifiedName,
    ModelInfo,
    SortedDict,
)
from erdantic.exceptions import UnresolvableForwardRefError
from erdantic.plugins import register_plugin
from erdantic.plugins.pydantic import is_pydantic_model


class FieldInfoWithDefault(FieldInfo):
    default_value: str

    _dot_row_template = (
        """<tr>"""
        """<td>{name}</td>"""
        """<td>{type_name}</td>"""
        """<td port="{name}" width="36">{default_value}</td>"""
        """</tr>"""
    )

    @classmethod
    def from_raw_type(
        cls, model_full_name: FullyQualifiedName, name: str, raw_type: type, raw_default_value: Any
    ) -> Self:
        default_value = (
            "" if raw_default_value is pydantic_core.PydanticUndefined else repr(raw_default_value)
        )
        field_info = cls(
            model_full_name=model_full_name,
            name=name,
            type_name=typenames(raw_type, remove_modules=REMOVE_ALL_MODULES),
            default_value=default_value,
        )
        field_info._raw_type = raw_type
        return field_info

    def to_dot_row(self) -> str:
        return self._dot_row_template.format(
            name=self.name,
            type_name=self.type_name,
            default_value=escape(self.default_value),  # Escape HTML-unsafe characters
        )


class ModelInfoWithDefault(ModelInfo):
    fields: Dict[str, FieldInfoWithDefault] = {}


class EntityRelationshipDiagramWithDefault(EntityRelationshipDiagram):
    models: SortedDict[str, ModelInfoWithDefault] = SortedDict()


def get_fields_from_pydantic_model_with_default(model) -> List[FieldInfoWithDefault]:
    try:
        # Rebuild model schema to resolve forward references
        model.model_rebuild()
    except pydantic.errors.PydanticUndefinedAnnotation as e:
        model_full_name = FullyQualifiedName.from_object(model)
        forward_ref = e.name
        msg = (
            f"Failed to resolve forward reference '{forward_ref}' in the type annotations for "
            f"Pydantic model {model_full_name}. "
            "You should use the model's model_rebuild() method to manually resolve it."
        )
        raise UnresolvableForwardRefError(
            msg, name=forward_ref, model_full_name=model_full_name
        ) from e
    return [
        FieldInfoWithDefault.from_raw_type(
            model_full_name=FullyQualifiedName.from_object(model),
            name=name,
            # typing special forms currently get typed as object
            # https://github.com/python/mypy/issues/9773
            raw_type=pydantic_field_info.annotation or Any,  # type: ignore
            raw_default_value=pydantic_field_info.default,
        )
        for name, pydantic_field_info in model.model_fields.items()
    ]


register_plugin("pydantic", is_pydantic_model, get_fields_from_pydantic_model_with_default)
