import pytest
from rest_framework.exceptions import ValidationError

from web_forms.submissions.api.fields import SemicolonSeparatedEmailField


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (
            "test1@example.com;test2@example.com",
            ["test1@example.com", "test2@example.com"],
        ),
        (
            " test1@example.com ; test2@example.com ",
            ["test1@example.com", "test2@example.com"],
        ),
        (
            "test1@example.com;;test2@example.com",
            ["test1@example.com", "test2@example.com"],
        ),
        ("test1@example.com;", ["test1@example.com"]),
        ("", []),
    ],
)
def test_to_internal_value_valid(input_value, expected_output):
    field = SemicolonSeparatedEmailField()
    assert field.to_internal_value(input_value) == expected_output


@pytest.mark.parametrize(
    "input_value",
    [
        (12345),
        (["test@example.com"]),
    ],
)
def test_to_internal_value_invalid_type(input_value):
    field = SemicolonSeparatedEmailField()
    with pytest.raises(ValidationError) as excinfo:
        field.to_internal_value(input_value)
    assert "This field must be a string." in str(excinfo.value)


@pytest.mark.parametrize(
    "input_value",
    [
        ("test1@example.com;invalid-email"),
        ("invalid-email"),
    ],
)
def test_to_internal_value_invalid_email(input_value):
    field = SemicolonSeparatedEmailField()
    with pytest.raises(ValidationError) as excinfo:
        field.to_internal_value(input_value)
    print("DUPA", str(excinfo.value))
    assert "Enter a valid email address" in str(excinfo.value)


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (
            ["test1@example.com", "test2@example.com"],
            "test1@example.com;test2@example.com",
        ),
        (
            [" test1@example.com ", " test2@example.com "],
            "test1@example.com;test2@example.com",
        ),
        (["test1@example.com"], "test1@example.com"),
        ([], ""),
    ],
)
def test_to_representation_valid(input_value, expected_output):
    field = SemicolonSeparatedEmailField()
    assert field.to_representation(input_value) == expected_output


@pytest.mark.parametrize(
    "input_value",
    [
        ("test1@example.com;test2@example.com"),
        (12345),
    ],
)
def test_to_representation_invalid_type(input_value):
    field = SemicolonSeparatedEmailField()
    with pytest.raises(ValidationError) as excinfo:
        field.to_representation(input_value)
    assert "This field must be a list." in str(excinfo.value)
