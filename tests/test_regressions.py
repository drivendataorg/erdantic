import sys
from typing import Optional

from pydantic import BaseModel
import pytest

import erdantic as erd


class Core(BaseModel):
    """Used in test_153_child_class_forward_ref"""

    data: object
    part: Optional[list["Part"]] = None


class Part(Core):
    """Used in test_153_child_class_forward_ref"""


# Unclear why Pydantic doesn't rebuild correctly for Python 3.10 and earlier
@pytest.mark.skipif(sys.version_info < (3, 11), reason="Passes for Python 3.11+")
def test_153_child_class_forward_ref():
    """
    Test that inherited forward reference on child class is handled correctly.
    https://github.com/drivendataorg/erdantic/issues/153
    """

    # Should not raise UnevaluatedForwardRefError
    erd.create(Core)
