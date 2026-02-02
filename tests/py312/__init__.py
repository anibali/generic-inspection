import sys

import pytest

if sys.version_info < (3, 12):  # noqa: UP036
    pytest.skip("Test requires Python >= 3.12", allow_module_level=True)
