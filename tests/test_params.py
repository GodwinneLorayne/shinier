import inspect

import pytest
from shinier.params import (
    ParameterKind,
    convert_parameter_kind,
    inspect_callable,
)


def test_convert_parameter_kind():
    if hasattr(inspect.Parameter, "POSITIONAL_ONLY"):
        assert (
            convert_parameter_kind(getattr(inspect.Parameter, "POSITIONAL_ONLY"))
            == ParameterKind.POSITIONAL_ONLY
        )

    if hasattr(inspect.Parameter, "POSITIONAL_OR_KEYWORD"):
        assert (
            convert_parameter_kind(getattr(inspect.Parameter, "POSITIONAL_OR_KEYWORD"))
            == ParameterKind.POSITIONAL_OR_KEYWORD
        )

    if hasattr(inspect.Parameter, "VAR_POSITIONAL"):
        assert (
            convert_parameter_kind(getattr(inspect.Parameter, "VAR_POSITIONAL"))
            == ParameterKind.VAR_POSITIONAL
        )

    if hasattr(inspect.Parameter, "KEYWORD_ONLY"):
        assert (
            convert_parameter_kind(getattr(inspect.Parameter, "KEYWORD_ONLY"))
            == ParameterKind.KEYWORD_ONLY
        )

    if hasattr(inspect.Parameter, "VAR_KEYWORD"):
        assert (
            convert_parameter_kind(getattr(inspect.Parameter, "VAR_KEYWORD"))
            == ParameterKind.VAR_KEYWORD
        )

    with pytest.raises(ValueError):
        convert_parameter_kind("Not a valid parameter kind")


def test_inspect_callable_no_params_no_return():
    def func():
        pass

    signature = inspect_callable(func)

    assert signature.return_annotation is None
    assert signature.parameters == []


def test_inspect_callable_no_params_with_return():
    def func() -> int:
        return 5

    signature = inspect_callable(func)

    assert signature.return_annotation and signature.return_annotation.annotation == int
    assert signature.parameters == []


def test_inspect_callable_with_params_no_return():
    def func(a: int, b: str):
        pass

    signature = inspect_callable(func)

    assert signature.return_annotation is None
    assert len(signature.parameters) == 2

    assert signature.parameters[0].name == "a"
    assert signature.parameters[0].kind == ParameterKind.POSITIONAL_OR_KEYWORD

    assert signature.parameters[1].name == "b"
    assert signature.parameters[1].kind == ParameterKind.POSITIONAL_OR_KEYWORD


def test_inspect_callable_with_params_with_return():
    def func(a: int, b: str) -> int:
        return 5

    signature = inspect_callable(func)

    assert signature.return_annotation and signature.return_annotation.annotation == int
    assert len(signature.parameters) == 2

    assert signature.parameters[0].name == "a"
    assert signature.parameters[0].kind == ParameterKind.POSITIONAL_OR_KEYWORD

    assert signature.parameters[1].name == "b"
    assert signature.parameters[1].kind == ParameterKind.POSITIONAL_OR_KEYWORD


def test_inspect_callable_with_params_with_return_var_positional():
    def func(a: int, *b: str) -> int:
        return 5

    signature = inspect_callable(func)

    assert signature.return_annotation and signature.return_annotation.annotation == int
    assert len(signature.parameters) == 2

    assert signature.parameters[0].name == "a"
    assert signature.parameters[0].kind == ParameterKind.POSITIONAL_OR_KEYWORD

    assert signature.parameters[1].name == "b"
    assert signature.parameters[1].kind == ParameterKind.VAR_POSITIONAL


def test_inspect_callable_with_params_with_return_keyword_only():
    def func(*, a: int, b: str) -> int:
        return 5

    signature = inspect_callable(func)

    assert signature.return_annotation and signature.return_annotation.annotation == int
    assert len(signature.parameters) == 2

    assert signature.parameters[0].name == "a"
    assert signature.parameters[0].kind == ParameterKind.KEYWORD_ONLY

    assert signature.parameters[1].name == "b"
    assert signature.parameters[1].kind == ParameterKind.KEYWORD_ONLY


def test_inspect_callable_with_params_with_return_var_keyword():
    def func(**kwargs: str) -> int:
        return 5

    signature = inspect_callable(func)

    assert signature.return_annotation and signature.return_annotation.annotation == int
    assert len(signature.parameters) == 1

    assert signature.parameters[0].name == "kwargs"
    assert signature.parameters[0].kind == ParameterKind.VAR_KEYWORD


def test_inspect_callable_with_params_with_return_positional_only():
    def func(a: int, /) -> int:
        return 5

    signature = inspect_callable(func)

    assert signature.return_annotation and signature.return_annotation.annotation == int
    assert len(signature.parameters) == 1

    assert signature.parameters[0].name == "a"
    assert signature.parameters[0].kind == ParameterKind.POSITIONAL_ONLY
