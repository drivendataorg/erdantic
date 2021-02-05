import pytest

from erdantic.erd import Field, Model


def test_abstract_field_instatiation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Field()


def test_abstract_model_instation():
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        Model()
