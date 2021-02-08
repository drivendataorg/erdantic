import pytest

import erdantic as erd
from erdantic.examples.pydantic import Party
from erdantic.base import Adapter, Field, Model, register_adapter


def test_abstract_field_instatiation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Field()


def test_abstract_model_instantiation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Model()


def test_adapter_registration():
    # Incomplete implementation
    class IncompleteAdapter(Adapter):
        pass

    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        register_adapter("incomplete")(IncompleteAdapter)

    # Not a subclass
    class UsbAdapter:
        pass

    with pytest.raises(ValueError, match=r"Only subclasses of Adapter can be registered"):
        register_adapter("usb")(UsbAdapter)


def test_repr():
    diagram = erd.create(Party)
    assert repr(diagram.models[0]) and isinstance(repr(diagram.models[0]), str)
    assert repr(diagram.models[0].fields[0]) and isinstance(repr(diagram.models[0].fields[0]), str)
