import typing
from typing import Annotated, Generic, TypeVar

from generic_inspection import infer_generic_args

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def test_generic_alias_with_one_type_var() -> None:
    class A(Generic[T]): ...

    assert infer_generic_args(A, A[U]) == (U,)  # type: ignore[valid-type]


def test_generic_alias_with_one_concrete_type() -> None:
    class A(Generic[T]): ...

    assert infer_generic_args(A, A[int]) == (int,)


def test_subclass_with_one_type_var() -> None:
    class A(Generic[T]): ...

    class B(A[U]): ...

    assert infer_generic_args(A, B) == (U,)


def test_subclass_with_one_concrete_type() -> None:
    class A(Generic[T]): ...

    class B(A[int]): ...

    assert infer_generic_args(A, B) == (int,)


def test_subclass_with_one_annotated_concrete_type() -> None:
    class A(Generic[T]): ...

    class B(A[Annotated[int, "hey"]]): ...

    assert infer_generic_args(A, B) == (Annotated[int, "hey"],)


def test_generic_alias_with_reordered_concrete_types() -> None:
    class A(Generic[T, U]): ...

    class B(A[V, U], Generic[U, V]): ...

    assert infer_generic_args(A, B[int, str]) == (str, int)


def test_subclass_with_reordered_concrete_types() -> None:
    class A(Generic[T, U]): ...

    class B(A[V, U], Generic[U, V]): ...

    class C(B[int, str]): ...

    assert infer_generic_args(A, C) == (str, int)


def test_generic_alias_with_complex_inheritance() -> None:
    class A(Generic[T]): ...

    class B(A[T]): ...

    class C(Generic[U]): ...

    class D(B[V], C[int], list[U], Generic[U, V]): ...

    assert infer_generic_args(A, D[int, str]) == (str,)


def test_subclass_with_skinny_inheritance() -> None:
    class A(Generic[T]): ...

    class B(A[int]): ...

    class C(B): ...

    assert infer_generic_args(A, C) == (int,)


def test_subclass_with_broken_chain() -> None:
    class A(Generic[T]): ...

    class B(A): ...  # type: ignore[type-arg]

    assert infer_generic_args(A, B) == (T,)


def test_subclass_instance_with_one_concrete_type() -> None:
    class A(Generic[T]): ...

    class B(A[int]): ...

    b = B()

    assert infer_generic_args(A, b) == (int,)


def test_generic_alias_instance_with_one_concrete_type() -> None:
    class A(Generic[T]): ...

    a = A[int]()

    assert infer_generic_args(A, a) == (int,)


def test_subclass_is_base_class_with_one_type_var() -> None:
    class A(Generic[T]): ...

    assert infer_generic_args(A, A) == (T,)


def test_generic_alias_is_base_class_with_one_concrete_type() -> None:
    class A(Generic[T]): ...

    a = A[int]()

    assert infer_generic_args(A, a) == (int,)


def test_builtin_list_as_base_class() -> None:
    class A(list[str]): ...

    assert infer_generic_args(list, A) == (str,)


def test_typing_list_as_base_class() -> None:
    class A(typing.List[str]): ...  # noqa: UP006

    assert infer_generic_args(list, A) == (str,)


def test_builtin_dict() -> None:
    assert infer_generic_args(dict, dict[str, int]) == (str, int)


def test_typing_dict() -> None:
    assert infer_generic_args(typing.Dict, typing.Dict[str, int]) == (str, int)  # noqa: UP006
