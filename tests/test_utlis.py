import pytest

from web_forms.utils import format_dict_for_email


def test_format_dict_for_email_with_invalid_input():
    with pytest.raises(ValueError, match="Input must be a dictionary"):
        format_dict_for_email(["not", "a", "dictionary"])


def test_format_dict_for_email_with_empty_dict():
    result = format_dict_for_email({})
    expected_output = "<h2>Submission Details</h2>\n<ul>\n</ul>"
    assert result == expected_output


def test_format_dict_for_email_with_typical_data():
    data_dict = {
        "name": "John Doe",
        "email": "john@example.com",
        "message": "Hello, this is a test message.",
    }
    result = format_dict_for_email(data_dict)
    expected_output = (
        "<h2>Submission Details</h2>\n<ul>"
        "\n<li><strong>Name:</strong> John Doe</li>"
        "\n<li><strong>Email:</strong> john@example.com</li>"
        "\n<li><strong>Message:</strong> Hello, this is a test message.</li>"
        "\n</ul>"
    )
    assert result == expected_output


def test_format_dict_for_email_with_underscores_in_keys():
    data_dict = {
        "first_name": "John",
        "last_name": "Doe",
        "email_address": "john@example.com",
    }
    result = format_dict_for_email(data_dict)
    expected_output = (
        "<h2>Submission Details</h2>\n<ul>"
        "\n<li><strong>First Name:</strong> John</li>"
        "\n<li><strong>Last Name:</strong> Doe</li>"
        "\n<li><strong>Email Address:</strong> john@example.com</li>"
        "\n</ul>"
    )
    assert result == expected_output


def test_format_dict_for_email_with_newline_in_values():
    data_dict = {"name": "John Doe", "message": "Hello,\nthis is a test message."}
    result = format_dict_for_email(data_dict)
    expected_output = (
        "<h2>Submission Details</h2>\n<ul>"
        "\n<li><strong>Name:</strong> John Doe</li>"
        "\n<li><strong>Message:</strong> Hello,<br>this is a test message.</li>"
        "\n</ul>"
    )
    assert result == expected_output
