from typing import Generic, Protocol, TypeVar

from generic_inspection import get_generic_params

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)


def test_non_generic_class() -> None:
    class A: ...

    assert get_generic_params(A) == ()


def test_generic_class() -> None:
    class A(Generic[T]): ...

    assert get_generic_params(A) == (T,)


def test_generic_class_with_two_type_vars() -> None:
    class A(Generic[T, U]): ...

    assert get_generic_params(A) == (T, U)


def test_generic_class_with_multiple_indirect_type_vars() -> None:
    class A(Generic[T, U]): ...

    class B(Generic[T, V]): ...

    class C(A[T, U], B[T, V]): ...

    assert get_generic_params(C) == (T, U, V)


def test_generic_class_partially_defined() -> None:
    class A(Generic[T, U]): ...

    class B(Generic[T, V]): ...

    class C: ...

    class D(A[T, float], B[bool, V], C): ...

    assert get_generic_params(D) == (T, V)


def test_generic_protocol_with_two_type_vars() -> None:
    class A(Protocol[T_co, U_co]): ...

    assert get_generic_params(A) == (T_co, U_co)


def test_generic_mixed_with_multiple_indirect_type_vars() -> None:
    class A(Protocol[T_co, U_co]): ...

    class B(Generic[T, V]): ...

    class C(A[T, U], B[T, V]): ...

    assert get_generic_params(C) == (T, U, V)
