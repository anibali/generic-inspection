import sys

import pytest

if sys.version_info < (3, 11):  # noqa: UP036
    pytest.skip("Test requires Python >= 3.11", allow_module_level=True)
