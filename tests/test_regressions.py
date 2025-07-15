from pydantic import BaseModel

import erdantic as erd


class Core(BaseModel):
    part: list["Part"]


class Part(Core):
    pass


def test_153_child_class_forward_ref():
    """
    Test that inherited forward reference on child class is handled correctly.
    https://github.com/drivendataorg/erdantic/issues/153
    """

    # Should not raise UnevaluatedForwardRefError
    erd.create(Core)
