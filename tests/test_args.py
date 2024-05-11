from shinier.args import (
    Assignment,
    Flag,
    Value,
    is_kebab_case,
    is_snake_case,
    parse_arguments,
    parse_double_dash_assignment,
    parse_double_dash_flag,
    parse_single_dash_assignment,
    parse_single_dash_flag,
)


def test_is_kebab_case():
    assert is_kebab_case("kebab-case")
    assert is_kebab_case("kebab-case-kebab-case")
    assert not is_kebab_case("")
    assert not is_kebab_case("snake_case")
    assert not is_kebab_case("camelCase")
    assert not is_kebab_case("PascalCase")
    assert not is_kebab_case("UPPER_CASE")
    assert not is_kebab_case("Title Case")
    assert not is_kebab_case("Sentence case")
    assert not is_kebab_case("kebab-case-")
    assert not is_kebab_case("-kebab-case")
    assert not is_kebab_case("kebab--case")


def test_is_snake_case():
    assert is_snake_case("snake_case")
    assert is_snake_case("snake_case_snake_case")
    assert not is_snake_case("")
    assert not is_snake_case("kebab-case")
    assert not is_snake_case("camelCase")
    assert not is_snake_case("PascalCase")
    assert not is_snake_case("UPPER_CASE")
    assert not is_snake_case("Title Case")
    assert not is_snake_case("Sentence case")
    assert not is_snake_case("snake_case_")
    assert not is_snake_case("_snake_case")
    assert not is_snake_case("snake__case")


def test_parse_single_dash_flag():
    assert list(parse_single_dash_flag("-c")) == [
        Flag(sentinel="-", name="c", full="-c")
    ]
    assert list(parse_single_dash_flag("-")) == []
    assert list(parse_single_dash_flag("-c=5")) == []
    assert list(parse_single_dash_flag("")) == []
    assert list(parse_single_dash_flag("-5")) == []
    assert list(parse_single_dash_flag("value")) == []


def test_parse_double_dash_flag():
    assert list(parse_double_dash_flag("--long")) == [
        Flag(sentinel="--", name="long", full="--long")
    ]
    assert list(parse_double_dash_flag("--5long")) == []
    assert list(parse_double_dash_flag("--")) == []
    assert list(parse_double_dash_flag("")) == []
    assert list(parse_double_dash_flag("-long")) == []
    assert list(parse_double_dash_flag("-long=5")) == []
    assert list(parse_double_dash_flag("--a!=")) == []
    assert list(parse_double_dash_flag("--long=5")) == []
    assert list(parse_double_dash_flag("--multi-word-flag")) == [
        Flag(sentinel="--", name="multi-word-flag", full="--multi-word-flag")
    ]
    assert list(parse_double_dash_flag("--multi-word-flag=5")) == []
    assert list(parse_double_dash_flag("--mixed_case-flag")) == []
    assert list(parse_double_dash_flag("--snake_case_flag")) == [
        Flag(sentinel="--", name="snake_case_flag", full="--snake_case_flag")
    ]
    assert list(parse_double_dash_flag("value")) == []


def test_parse_single_dash_assignment():
    assert list(parse_single_dash_assignment("-c=5")) == [
        Assignment(
            sentinel="-", name="c", flag="-c", delimiter="=", value="5", full="-c=5"
        )
    ]
    assert list(parse_single_dash_assignment("-c")) == []
    assert list(parse_single_dash_assignment("-")) == []
    assert list(parse_single_dash_assignment("-c 5")) == []
    assert list(parse_single_dash_assignment("")) == []
    assert list(parse_single_dash_assignment("-5")) == []
    assert list(parse_single_dash_assignment("-c=")) == [
        Assignment(
            sentinel="-", name="c", flag="-c", delimiter="=", value="", full="-c="
        )
    ]
    assert list(parse_single_dash_assignment("-5=")) == []
    assert list(parse_single_dash_assignment("value")) == []


def test_parse_double_dash_assignment():
    assert list(parse_double_dash_assignment("--long=5")) == [
        Assignment(
            sentinel="--",
            name="long",
            flag="--long",
            delimiter="=",
            value="5",
            full="--long=5",
        )
    ]
    assert list(parse_double_dash_assignment("--long")) == []
    assert list(parse_double_dash_assignment("--")) == []
    assert list(parse_double_dash_assignment("-long")) == []
    assert list(parse_double_dash_assignment("-long=5")) == []
    assert list(parse_double_dash_assignment("--5long")) == []
    assert list(parse_double_dash_assignment("--a!=")) == []
    assert list(parse_double_dash_assignment("--multi-word-flag=5")) == [
        Assignment(
            sentinel="--",
            name="multi-word-flag",
            flag="--multi-word-flag",
            delimiter="=",
            value="5",
            full="--multi-word-flag=5",
        )
    ]
    assert list(parse_double_dash_assignment("--multi-word-flag")) == []
    assert list(parse_double_dash_assignment("")) == []
    assert list(parse_double_dash_assignment("value")) == []


def test_parse_arguments():
    assert list(parse_arguments(["-c", "--long", "-c=5", "--long=5"])) == [
        Flag(sentinel="-", name="c", full="-c"),
        Flag(sentinel="--", name="long", full="--long"),
        Assignment(
            sentinel="-", name="c", flag="-c", delimiter="=", value="5", full="-c=5"
        ),
        Assignment(
            sentinel="--",
            name="long",
            flag="--long",
            delimiter="=",
            value="5",
            full="--long=5",
        ),
    ]
    assert list(
        parse_arguments(
            [
                "-c",
                "--long",
                "-c=5",
                "--long=5",
                "--multi-word-flag=5",
                "--snake_case_flag",
            ]
        )
    ) == [
        Flag(sentinel="-", name="c", full="-c"),
        Flag(sentinel="--", name="long", full="--long"),
        Assignment(
            sentinel="-", name="c", flag="-c", delimiter="=", value="5", full="-c=5"
        ),
        Assignment(
            sentinel="--",
            name="long",
            flag="--long",
            delimiter="=",
            value="5",
            full="--long=5",
        ),
        Assignment(
            sentinel="--",
            name="multi-word-flag",
            flag="--multi-word-flag",
            delimiter="=",
            value="5",
            full="--multi-word-flag=5",
        ),
        Flag(sentinel="--", name="snake_case_flag", full="--snake_case_flag"),
    ]
    assert list(
        parse_arguments(
            [
                "-c",
                "--long",
                "-c=5",
                "--long=5",
                "--multi-word-flag=5",
                "--snake_case_flag",
                "-c=5",
                "--long=5",
                "--multi-word-flag=5",
                "--snake_case_flag",
            ]
        )
    ) == [
        Flag(sentinel="-", name="c", full="-c"),
        Flag(sentinel="--", name="long", full="--long"),
        Assignment(
            sentinel="-", name="c", flag="-c", delimiter="=", value="5", full="-c=5"
        ),
        Assignment(
            sentinel="--",
            name="long",
            flag="--long",
            delimiter="=",
            value="5",
            full="--long=5",
        ),
        Assignment(
            sentinel="--",
            name="multi-word-flag",
            flag="--multi-word-flag",
            delimiter="=",
            value="5",
            full="--multi-word-flag=5",
        ),
        Flag(sentinel="--", name="snake_case_flag", full="--snake_case_flag"),
        Assignment(
            sentinel="-", name="c", flag="-c", delimiter="=", value="5", full="-c=5"
        ),
        Assignment(
            sentinel="--",
            name="long",
            flag="--long",
            delimiter="=",
            value="5",
            full="--long=5",
        ),
        Assignment(
            sentinel="--",
            name="multi-word-flag",
            flag="--multi-word-flag",
            delimiter="=",
            value="5",
            full="--multi-word-flag=5",
        ),
        Flag(sentinel="--", name="snake_case_flag", full="--snake_case_flag"),
    ]
    assert list(
        parse_arguments(
            [
                "-c",
                "--long",
                "-c=5",
                "--long=5",
                "--multi-word-flag=5",
                "--snake_case_flag",
                "-c=5",
                "--long=5",
                "--multi-word-flag=5",
                "--snake_case_flag",
                "value",
            ]
        )
    ) == [
        Flag(sentinel="-", name="c", full="-c"),
        Flag(sentinel="--", name="long", full="--long"),
        Assignment(
            sentinel="-", name="c", flag="-c", delimiter="=", value="5", full="-c=5"
        ),
        Assignment(
            sentinel="--",
            name="long",
            flag="--long",
            delimiter="=",
            value="5",
            full="--long=5",
        ),
        Assignment(
            sentinel="--",
            name="multi-word-flag",
            flag="--multi-word-flag",
            delimiter="=",
            value="5",
            full="--multi-word-flag=5",
        ),
        Flag(sentinel="--", name="snake_case_flag", full="--snake_case_flag"),
        Assignment(
            sentinel="-", name="c", flag="-c", delimiter="=", value="5", full="-c=5"
        ),
        Assignment(
            sentinel="--",
            name="long",
            flag="--long",
            delimiter="=",
            value="5",
            full="--long=5",
        ),
        Assignment(
            sentinel="--",
            name="multi-word-flag",
            flag="--multi-word-flag",
            delimiter="=",
            value="5",
            full="--multi-word-flag=5",
        ),
        Flag(sentinel="--", name="snake_case_flag", full="--snake_case_flag"),
        Value(value="value", full="value"),
    ]
