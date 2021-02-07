import pytest

import erdantic as erd
from erdantic.examples.pydantic import Party
from erdantic.base import DiagramFactory, Field, Model, register_factory


def test_abstract_field_instatiation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Field()


def test_abstract_model_instantiation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Model()


def test_diagram_factory_registration():
    # Incomplete implementation
    class IncompleteDiagramFactory(DiagramFactory):
        pass

    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        register_factory("incomplete")(IncompleteDiagramFactory)

    # Not a subclass
    class DiagramFarm:
        pass

    with pytest.raises(ValueError, match=r"Only subclasses of DiagramFactory can be registered"):
        register_factory("potato")(DiagramFarm)


def test_repr():
    diagram = erd.create(Party)
    assert repr(diagram.models[0]) and isinstance(repr(diagram.models[0]), str)
    assert repr(diagram.models[0].fields[0]) and isinstance(repr(diagram.models[0].fields[0]), str)
