from generic_inspection import infer_generic_args


def test_pep695() -> None:
    class A[T]: ...

    class B[T](A[T]): ...

    class C[T]: ...

    class D[U, Z](B[Z], C[int], list[U]): ...

    assert infer_generic_args(A, D[int, str]) == (str,)
    assert infer_generic_args(B, D[int, str]) == (str,)
    assert infer_generic_args(C, D[int, str]) == (int,)
    assert infer_generic_args(list, D[int, str]) == (int,)
