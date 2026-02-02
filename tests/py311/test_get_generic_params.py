from typing import Generic, TypeVar, TypeVarTuple

from generic_inspection import get_generic_params

T = TypeVar("T")
U = TypeVar("U")
Ts = TypeVarTuple("Ts")


def test_generic_class_only_variadic() -> None:
    class A(Generic[*Ts]): ...

    assert get_generic_params(A) == (Ts,)


def test_generic_class_partially_variadic() -> None:
    class A(Generic[T, *Ts, U]): ...

    assert get_generic_params(A) == (T, Ts, U)
