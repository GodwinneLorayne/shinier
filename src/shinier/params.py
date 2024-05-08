"""Callable Parameter inspection for Shinier"""

from typing import Annotated, Optional, Union, Callable, Iterator, Sequence, Iterable, Any, Type
from enum import Enum, unique, auto
import inspect

from pydantic import BaseModel, Field

# ==========================================================================================
#                         Constants
# ==========================================================================================

DIGITS = "0123456789"

# ==========================================================================================
#                         Enums
# ==========================================================================================

@unique
class ParameterKind(Enum):
    """The 'kind' of parameter"""
    POSITIONAL_ONLY = auto()
    POSITIONAL_OR_KEYWORD = auto()
    VAR_POSITIONAL = auto()
    KEYWORD_ONLY = auto()
    VAR_KEYWORD = auto()

# ==========================================================================================
#                         Models
# ==========================================================================================

class Parameter(BaseModel):
    """A callable parameter"""

    name: Annotated[str, Field(description="The name of the parameter")]
    kind: Annotated[ParameterKind, Field(description="The kind of parameter")]
    default: Annotated[Any, Field(description="The default value of the parameter")]
    annotation: Annotated[Type, Field(description="The annotation of the parameter")]

class ReturnAnnotation(BaseModel):
    """A callable return"""

    annotation: Annotated[Type, Field(description="The annotation of the return")]

class Signature(BaseModel):
    """A callable signature"""

    parameters: Annotated[Sequence[Parameter], Field(description="The parameters of the callable")]
    return_annotation: Annotated[Optional[ReturnAnnotation], Field(description="The return annotation of the callable")]

# ==========================================================================================
#                        Free Functions
# ==========================================================================================

def convert_parameter_kind(kind: Any) -> ParameterKind:
    """Convert a ParameterKind from inspect to ParameterKind"""

    # By using hasattr and getattr, we can avoid the error if the attribute is not present, without having to check specific python versions
    if hasattr(inspect.Parameter, "POSITIONAL_ONLY") and kind == getattr(inspect.Parameter, "POSITIONAL_ONLY"):
        return ParameterKind.POSITIONAL_ONLY

    if hasattr(inspect.Parameter, "POSITIONAL_OR_KEYWORD") and kind == getattr(inspect.Parameter, "POSITIONAL_OR_KEYWORD"):
        return ParameterKind.POSITIONAL_OR_KEYWORD

    if hasattr(inspect.Parameter, "VAR_POSITIONAL") and kind == getattr(inspect.Parameter, "VAR_POSITIONAL"):
        return ParameterKind.VAR_POSITIONAL

    if hasattr(inspect.Parameter, "KEYWORD_ONLY") and kind == getattr(inspect.Parameter, "KEYWORD_ONLY"):
        return ParameterKind.KEYWORD_ONLY

    if hasattr(inspect.Parameter, "VAR_KEYWORD") and kind == getattr(inspect.Parameter, "VAR_KEYWORD"):
        return ParameterKind.VAR_KEYWORD

    else:
        raise ValueError(f"Unknown ParameterKind: {kind}")

def inspect_callable(func: Callable) -> Signature:
    """Inspect a Callable and return its Signature"""

    if not func:
        raise ValueError("func is None")
    
    if not callable(func):
        raise ValueError("func is not callable")

    inspect_signature = inspect.signature(func)

    if inspect_signature.return_annotation == inspect.Signature.empty:
        return_annotation = None
    else:
        return_annotation = ReturnAnnotation(annotation=inspect_signature.return_annotation)

    parameters = [
        Parameter(
            name=parameter.name,
            kind=convert_parameter_kind(parameter.kind),
            default=parameter.default,
            annotation=parameter.annotation
        )
        for parameter in inspect_signature.parameters.values()
    ]

    return Signature(parameters=parameters, return_annotation=return_annotation)