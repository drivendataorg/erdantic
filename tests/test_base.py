import pytest

import erdantic as erd
from erdantic.base import Field, Model, register_model_adapter
from erdantic.examples.pydantic import Party
from erdantic.exceptions import InvalidModelAdapterError


def test_abstract_field_instatiation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Field()


def test_abstract_model_instantiation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Model()


def test_model_adapter_registration_error():
    # Not a subclass
    class ModelAirplane:
        pass

    with pytest.raises(
        InvalidModelAdapterError, match=r"Only subclasses of erdantic.base.Model can be registered"
    ):
        register_model_adapter("airplane")(ModelAirplane)


def test_repr():
    diagram = erd.create(Party)
    assert repr(diagram.models[0]) and isinstance(repr(diagram.models[0]), str)
    assert repr(diagram.models[0].fields[0]) and isinstance(repr(diagram.models[0].fields[0]), str)
