# generic-inspection

Utilities for generic type inspection.
Supports Python 3.10+.

## Inferring specialised type arguments

Consider the following code:

```python
from typing import Generic, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")

class Machine(Generic[InputT, OutputT]):
    pass

class TextMachine(Machine[InputT, str]):
    pass

class NumberTextMachine(TextMachine[float]):
    pass
```

We can infer the specialised type arguments of a subclass
with respect to the class type parameters of a particular base class
using the `infer_generic_args` function.

```ipython
>>> infer_generic_args(Machine, NumberTextMachine)
(float, str)
```

The results here tell us that `InputT` is `float` and `OutputT` is `str`.

## Development environment

```bash
# Set up the virtual environment.
uv sync --frozen --all-groups
# Run tests.
just test
```

## Similar projects

- https://github.com/Hochfrequenz/python-generics

## License

```
Copyright 2026 Aiden Nibali

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
