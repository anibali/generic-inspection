"""Utilities for generic type inspection."""

import typing
from collections import deque
from collections.abc import Sequence
from typing import NamedTuple, TypeAlias, TypeVar, get_args, get_origin

import typing_extensions
from typing_extensions import get_original_bases
from typing_inspection.typing_objects import is_generic, is_typevar, is_typevartuple

GenericAlias: TypeAlias = typing.GenericAlias | typing._GenericAlias  # type: ignore[name-defined]  # noqa: SLF001
TypeLike: TypeAlias = type | GenericAlias


class _ClassHierarchyNode(NamedTuple):
    class_type: type
    type_args: tuple[TypeLike | TypeVar | tuple[TypeLike | TypeVar, ...], ...]


def get_type_params(obj: object, /) -> tuple[TypeVar, ...]:
    """Get type parameters for a generic, generic alias, or similar."""
    # See https://peps.python.org/pep-0695/#accessing-type-parameters-at-runtime
    if hasattr(obj, "__type_params__"):
        type_params = obj.__type_params__  # pyright: ignore[reportAttributeAccessIssue]
        assert isinstance(type_params, tuple)  # noqa: S101
        return type_params

    # See https://peps.python.org/pep-0585/#parameters-to-generics-are-available-at-runtime
    return getattr(obj, "__parameters__", ())


def get_orig_class(obj: object, /) -> TypeLike:
    """Get the type of an object, preferring the full generic alias if possible."""
    if hasattr(obj, "__orig_class__"):
        orig_class = obj.__orig_class__  # pyright: ignore[reportAttributeAccessIssue]
        assert isinstance(orig_class, TypeLike)  # noqa: S101
        return orig_class
    return type(obj)


def is_protocol(obj: object, /) -> bool:
    """Check whether the given object is exactly Protocol."""
    return obj is typing.Protocol or obj is typing_extensions.Protocol


def is_genericalias(obj: object, /) -> bool:
    """Check whether the given object is a GenericAlias."""
    return isinstance(obj, GenericAlias)


# This function is heavily based on `typing._collect_parameters`.
# We don't use that function directly since it is part of the internal typing API.
def collect_parameters(args: Sequence[type | tuple[TypeLike | TypeVar, ...] | TypeVar]) -> tuple[TypeVar, ...]:  # noqa: C901
    """Collect all type variables and parameter specifications in args in order of first appearance."""
    parameters = []
    for t in args:
        if isinstance(t, type):
            # We don't want __parameters__ descriptor of a bare Python class.
            pass
        elif isinstance(t, tuple):
            # `t` might be a tuple, when `ParamSpec` is substituted with
            # `[T, int]`, or `[int, *Ts]`, etc.
            for x in t:
                for collected in collect_parameters([x]):
                    if collected not in parameters:
                        parameters.append(collected)
        elif hasattr(t, "__typing_subst__"):
            if t not in parameters:
                parameters.append(t)
        else:
            for x in get_type_params(t):
                if x not in parameters:
                    parameters.append(x)
    return tuple(parameters)


def get_generic_params(t: type, /) -> tuple[TypeVar, ...]:
    """Get the type variables which parametrise a generic class.

    If the given class is not generic, an empty tuple will be returned.
    """
    bases = get_original_bases(t)
    # If Generic or Protocol is a base, it must include all type variables.
    # It determines the order of type parameters.
    for base in bases:
        base_origin = get_origin(base)
        if base_origin is not None and (is_generic(base_origin) or is_protocol(base_origin)):
            return get_type_params(base)

    # Otherwise, we must collect all unique TypeVar objects found in other bases.
    return collect_parameters(bases)


def align_type_args(
    type_params: tuple[TypeVar, ...],
    type_args: tuple[TypeLike | TypeVar | tuple[TypeLike | TypeVar, ...], ...],
) -> tuple[TypeLike | TypeVar | tuple[TypeLike | TypeVar, ...], ...]:
    """Align type arguments with type parameters.

    If the type parameters includes a `TypeVarTuple`,
    type arguments corresponding to that `TypeVarTuple`
    will be "grouped" into a tuple.

    Arguments:
        type_params: The type parameters.
        type_args: The type arguments.

    Returns:
        The aligned type arguments
        as a tuple with the same length as `type_params`.
    """
    if not type_args:
        return type_params

    # Calculate the number of type args that must be assigned to a TypeVarTuple,
    # under the assumption that there _is_ a TypeVarTuple
    # (which may not be true).
    num_variadic_type_args = (len(type_args) - len(type_params)) + 1

    # Align the given type args with the given type params
    # by grouping any type args that correspond to a TypeVarTuple.
    aligned_type_args: list[TypeLike | TypeVar | tuple[TypeLike | TypeVar, ...]] = []
    type_var_tuple_args: list[TypeLike | TypeVar] = []
    type_var_it = iter(type_params)
    type_var = next(type_var_it, None)
    for i, type_arg in enumerate(type_args):
        assert type_var is not None  # noqa: S101
        if is_typevartuple(type_var):  # Check whether we are processing a TypeVarTuple.
            if i - len(aligned_type_args) == num_variadic_type_args:
                aligned_type_args.append(tuple(type_var_tuple_args))
                type_var_tuple_args = []
                type_var = next(type_var_it, None)
            else:
                assert not isinstance(type_arg, tuple)  # noqa: S101
                type_var_tuple_args.append(type_arg)
                continue
        aligned_type_args.append(type_arg)
        type_var = next(type_var_it, None)

    # Special clean-up for when the last type param is a TypeVarTuple.
    if type_var is not None:
        aligned_type_args.append(tuple(type_var_tuple_args))

    if len(aligned_type_args) != len(type_params):
        msg = "Unable to align type arguments with type parameters"
        raise ValueError(msg)

    # Convert the aligned type args list into a tuple.
    return tuple(aligned_type_args)


def infer_generic_args(
    base_class: type,
    subclass_or_instance: object,
    /,
) -> tuple[TypeLike | TypeVar | tuple[TypeLike | TypeVar, ...], ...]:
    """Infer the generic arguments of a base class, as determined by one of its subclasses.

    If the subclass is generic and does not fulfill all of the base class's generic type variables,
    those generic arguments will be returned as ``TypeVar`` instances.

    Args:
        base_class: The generic base class to infer generic arguments for.
            Must have ``Generic`` as one of its base classes.
        subclass_or_instance: The subclass to trace type arguments from, or an instance of that subclass.

    Returns:
        A tuple of types and/or unfilled type variables
        that correspond to generic type parameters in the base class.
    """
    base_class = get_origin(base_class) or base_class

    if isinstance(subclass_or_instance, type) or is_genericalias(subclass_or_instance):
        subclass_type_like = subclass_or_instance
    else:
        subclass_type_like = get_orig_class(subclass_or_instance)

    if is_genericalias(subclass_type_like):
        initial_type_args = get_args(subclass_type_like)
        subclass_origin = get_origin(subclass_type_like)
        subclass_type = subclass_origin
    else:
        initial_type_args = ()
        subclass_type = subclass_type_like
    assert isinstance(subclass_type, type)  # noqa: S101

    if not issubclass(subclass_type, base_class):
        msg = f"{subclass_type_like} is not a subclass of base class {base_class}"
        raise TypeError(msg)

    stack = deque[_ClassHierarchyNode]()
    stack.append(_ClassHierarchyNode(subclass_type, initial_type_args))

    while stack:
        current = stack.pop()
        generic_type_params = get_generic_params(current.class_type)

        if generic_type_params:
            type_var_map = dict(
                zip(
                    generic_type_params,
                    align_type_args(generic_type_params, current.type_args),
                    strict=True,
                )
            )
        else:
            type_var_map = {}

        if current.class_type is base_class:
            # Support types like list and dict which do not register as having generic params.
            if not generic_type_params:
                return current.type_args
            # This final alignment ensures that TypeVarTuples receive a tuple of types/TypeVars.
            return tuple(type_var_map[e] for e in generic_type_params)

        for base in get_original_bases(current.class_type):
            base_origin = get_origin(base) or base
            if base_origin is not None and not is_generic(base_origin):
                filled_base_type_args = tuple(
                    type_var_map.get(base_type_arg, base_type_arg) if is_typevar(base_type_arg) else base_type_arg
                    for base_type_arg in get_args(base)
                )
                stack.append(_ClassHierarchyNode(base_origin, filled_base_type_args))

    msg = f"Unable to trace type arguments from {subclass_type_like} to {base_class}"
    raise ValueError(msg)
