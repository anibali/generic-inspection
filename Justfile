test-py python_version:
    uv run --isolated --frozen --active --python {{python_version}} --group test pytest

test-py310: (test-py "3.10")
test-py311: (test-py "3.11")
test-py312: (test-py "3.12")
test-py313: (test-py "3.13")

test-all: test-py310 test-py311 test-py312 test-py313

test:
    uv run pytest

lint:
    ruff check
    ruff format --check

type-check:
    mypy

check-all: lint type-check test-all
