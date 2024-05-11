"""Command-Line Argument Parsing for Shinier."""

from typing import Annotated, Callable, Iterable, Iterator, Union

from pydantic import BaseModel, Field

# ==========================================================================================
#                         Constants
# ==========================================================================================

DIGITS = "0123456789"
LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVwxyz"
ALPHA = LOWER + UPPER
ALNUM = ALPHA + DIGITS

# ==========================================================================================
#                         Models
# ==========================================================================================

# There are different types to express the syntax on the CLI
# What these values actually mean after being parsed is context-dependent


class Flag(BaseModel):
    """A command-line flag, Eg. -l or --long"""

    sentinel: Annotated[
        str,
        Field(
            description="Character(s) at the front which say this is a flag Eg. - or -- or /"
        ),
    ]
    name: Annotated[
        str,
        Field(
            description="Character(s) which make up the name of the flag Eg. l or long"
        ),
    ]
    full: Annotated[
        str,
        Field(description="Characters which make up the entire flag Eg. -l or --long"),
    ]


class Assignment(BaseModel):
    """A command-line flag+value, Eg. -l=5 or --length=5"""

    sentinel: Annotated[
        str,
        Field(
            description="Character(s) at the front which say this is an assignment Eg. ="
        ),
    ]
    name: Annotated[
        str,
        Field(
            description="Character(s) which make up the name of the flag Eg. l or length"
        ),
    ]
    flag: Annotated[
        str,
        Field(
            description="Character(s) which make up the entire flag Eg. -l or --length"
        ),
    ]
    delimiter: Annotated[
        str,
        Field(description="Character(s) which separate the flag from the value Eg. ="),
    ]
    value: Annotated[
        str, Field(description="Character(s) which make up the value Eg. 5")
    ]
    full: Annotated[
        str,
        Field(
            description="Characters which make up the entire assignment Eg. -l=5 or --length=5"
        ),
    ]


class Value(BaseModel):
    """A command-line value, Eg. 5"""

    value: Annotated[
        str, Field(description="Character(s) which make up the value Eg. 5")
    ]
    full: Annotated[
        str, Field(description="Characters which make up the entire value Eg. 5")
    ]


Argument = Union[Flag, Assignment, Value]
"""A parsed command-line argument, Eg. -l, --long, -l=5, --length=5, 5"""

Arguments = Iterable[Argument]
"""A list of parsed command-line arguments"""

ArgumentParser = Callable[[str], Iterator[Argument]]
"""A function which takes a string and returns an iterator of parsed command-line arguments"""

ArgumentParsers = Iterable[ArgumentParser]
"""A list of argument parser functions"""

InputArguments = Iterable[str]
"""A list of raw command-line arguments"""

# ==========================================================================================
#                         Functions
# ==========================================================================================


def is_kebab_case(input_string: str) -> bool:
    """Check if a string is in kebab-case"""

    if not input_string:
        return False

    if input_string[0] not in ALNUM:
        return False

    if input_string[-1] not in ALNUM:
        return False

    if "--" in input_string:
        return False

    trimmed = input_string.replace("-", "")

    return all(c in ALNUM for c in trimmed) and trimmed.islower()


def is_snake_case(input_string: str) -> bool:
    """Check if a string is in snake_case"""

    if not input_string:
        return False

    if input_string[0] not in ALNUM:
        return False

    if input_string[-1] not in ALNUM:
        return False

    if "__" in input_string:
        return False

    trimmed = input_string.replace("_", "")

    return all(c in ALNUM for c in trimmed) and trimmed.islower()


def parse_single_dash_flag(input_argument: str) -> Iterator[Argument]:
    """Parse a single dash argument, but only support one letter ascii flags Eg. -c but not -xfc"""

    if not input_argument.startswith("-"):
        return

    if len(input_argument) != 2:
        return

    if input_argument[1] not in ALPHA:
        return

    yield Flag(sentinel="-", name=input_argument[1], full=input_argument)


def parse_double_dash_flag(input_argument: str) -> Iterator[Argument]:
    """Parse a double dash argument, but only support flags not assignments Eg. --long but not --long=5

    Additionally, the flag must not start with a digit Eg. --5long"""

    if not input_argument.startswith("--"):
        return

    if len(input_argument) < 3:
        return

    if input_argument[2] not in ALPHA:
        return

    if "=" in input_argument:
        return

    name = input_argument[2:]

    if not (is_snake_case(name) or is_kebab_case(name)):
        return

    yield Flag(sentinel="--", name=name, full=input_argument)


def parse_single_dash_assignment(input_argument: str) -> Iterator[Argument]:
    """Parse a single dash argument, but only support one letter ascii flags with a value Eg. -c=5 but not -xfc=5 or -c 5

    Additionally, the value is permitted to be empty Eg. -c="""

    if not input_argument.startswith("-"):
        return

    if len(input_argument) < 3:
        return

    if input_argument[1] not in ALPHA:
        return

    if input_argument[2] != "=":
        return

    yield Assignment(
        sentinel="-",
        name=input_argument[1],
        flag=input_argument[:2],
        delimiter="=",
        value=input_argument[3:],
        full=input_argument,
    )


def parse_double_dash_assignment(input_argument: str) -> Iterator[Argument]:
    """Parse a double dash argument, but only support flags with a value Eg. --long=5 but not --long 5 or --long=5=5

    Additionally, the value is permitted to be empty Eg. --long="""

    if not input_argument.startswith("--"):
        return

    if len(input_argument) < 4:
        return

    if input_argument[2] not in ALPHA:
        return

    if "=" not in input_argument:
        return

    flag, value = input_argument.split("=", 1)

    name = flag[2:]

    if not (is_snake_case(name) or is_kebab_case(name)):
        return

    yield Assignment(
        sentinel="--",
        name=name,
        flag=flag,
        delimiter="=",
        value=value,
        full=input_argument,
    )


# ==========================================================================================
#                         Sane Defaults
# ==========================================================================================

DEFAULT_ARGUMENT_PARSERS: ArgumentParsers = [
    parse_double_dash_assignment,
    parse_single_dash_assignment,
    parse_double_dash_flag,
    parse_single_dash_flag,
]

# ==========================================================================================


def parse_arguments(
    input_arguments: InputArguments, parsers: ArgumentParsers = DEFAULT_ARGUMENT_PARSERS
) -> Arguments:
    """Parse a list of raw command-line arguments into a list of parsed command-line arguments"""

    # For each input argument, try to parse it with each parser
    for input_argument in input_arguments:
        for parser in parsers:
            # The first parser which successfully parses the argument wins
            parsed = False
            for argument in parser(input_argument):
                yield argument
                parsed = True

            if parsed:
                break
        else:
            # If no parser was able to parse the argument, treat it as a value
            yield Value(value=input_argument, full=input_argument)
