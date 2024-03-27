import subprocess
import textwrap

import pytest

import erdantic.examples
from erdantic.exceptions import PluginNotFoundError
from erdantic.plugins import (
    get_field_extractor_fn,
    get_predicate_fn,
    identify_field_extractor_fn,
    list_plugins,
    register_plugin,
)
import erdantic.plugins.attrs
import erdantic.plugins.dataclasses
import erdantic.plugins.pydantic


def test_register_plugin():
    """Custom plugin can be sucessfully registered and used."""

    class CustomBaseModel: ...

    def is_custom_model(obj):
        return (
            isinstance(obj, type)
            and issubclass(obj, CustomBaseModel)
            and obj is not CustomBaseModel
        )

    def get_fields_from_custom_model(model):
        return []

    register_plugin("test_plugin", is_custom_model, get_fields_from_custom_model)

    assert "test_plugin" in list_plugins()

    class MyModel(CustomBaseModel): ...

    assert identify_field_extractor_fn(MyModel) == get_fields_from_custom_model
    assert identify_field_extractor_fn(erdantic.examples.pydantic.Party) not in (
        get_fields_from_custom_model,
        None,
    )

    class NotAModel: ...

    assert identify_field_extractor_fn(NotAModel) is None


def test_get_predicate_fn():
    for key, predicate_fn in [
        ("attrs", erdantic.plugins.attrs.is_attrs_class),
        ("dataclasses", erdantic.plugins.dataclasses.is_dataclass_class),
        ("pydantic", erdantic.plugins.pydantic.is_pydantic_model),
        ("pydantic_v1", erdantic.plugins.pydantic.is_pydantic_v1_model),
    ]:
        assert get_predicate_fn(key) == predicate_fn

    with pytest.raises(PluginNotFoundError):
        get_predicate_fn("not_a_plugin")


def test_get_field_extractor_fn():
    for key, get_fields_fn in [
        ("attrs", erdantic.plugins.attrs.get_fields_from_attrs_class),
        ("dataclasses", erdantic.plugins.dataclasses.get_fields_from_dataclass),
        ("pydantic", erdantic.plugins.pydantic.get_fields_from_pydantic_model),
        ("pydantic_v1", erdantic.plugins.pydantic.get_fields_from_pydantic_v1_model),
    ]:
        assert get_field_extractor_fn(key) == get_fields_fn

    with pytest.raises(PluginNotFoundError):
        get_field_extractor_fn("not_a_plugin")


def test_identify_field_extractor_fn():
    for example_module, get_fields_fn in [
        (erdantic.examples.attrs, erdantic.plugins.attrs.get_fields_from_attrs_class),
        (erdantic.examples.dataclasses, erdantic.plugins.dataclasses.get_fields_from_dataclass),
        (erdantic.examples.pydantic, erdantic.plugins.pydantic.get_fields_from_pydantic_model),
        (
            erdantic.examples.pydantic_v1,
            erdantic.plugins.pydantic.get_fields_from_pydantic_v1_model,
        ),
    ]:
        assert identify_field_extractor_fn(example_module.Party) == get_fields_fn

    class NotAModel: ...

    assert identify_field_extractor_fn(NotAModel) is None


def test_core_plugins():
    """Core plugins are loaded when erdantic is imported."""
    for key in ("attrs", "dataclasses", "pydantic", "pydantic_v1"):
        script = textwrap.dedent(
            f"""\
            from erdantic.plugins import list_plugins
            assert "{key}" in list_plugins()
            """
        ).replace("\n", "; ")

        result = subprocess.run(
            ["python", "-c", script],
            capture_output=True,
            universal_newlines=True,
        )
        assert result.returncode == 0, result.stderr
