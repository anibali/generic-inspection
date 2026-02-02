from typing import Generic, TypeVar, TypeVarTuple, Unpack

from generic_inspection import infer_generic_args

T = TypeVar("T")

Ts = TypeVarTuple("Ts")


def test_subclass_with_concrete_types_and_variadic_base() -> None:
    class A(Generic[*Ts]): ...

    class B(A[int, str]): ...

    assert infer_generic_args(A, B) == ((int, str),)


def test_subclass_with_concrete_types_and_variadic_base_unpack() -> None:
    class A(Generic[Unpack[Ts]]): ...  # noqa: UP044

    class B(A[int, str]): ...

    assert infer_generic_args(A, B) == ((int, str),)


def test_subclass_with_concrete_types_and_trailing_variadic_base() -> None:
    class A(Generic[T, *Ts]): ...

    class B(A[bool, int, str]): ...

    assert infer_generic_args(A, B) == (bool, (int, str))


def test_subclass_with_concrete_types_and_leading_variadic_base() -> None:
    class A(Generic[*Ts, T]): ...

    class B(A[bool, int, str]): ...

    assert infer_generic_args(A, B) == ((bool, int), str)
