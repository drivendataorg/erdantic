from typing import Optional

from pydantic import BaseModel

import erdantic as erd


class Core(BaseModel):
    """Used in test_153_child_class_forward_ref"""

    data: object
    part: Optional[list["Part"]] = None


class Part(Core):
    """Used in test_153_child_class_forward_ref"""


def test_153_child_class_forward_ref():
    """
    Test that inherited forward reference on child class is handled correctly.
    https://github.com/drivendataorg/erdantic/issues/153
    """

    # Should not raise UnevaluatedForwardRefError
    erd.create(Core)
