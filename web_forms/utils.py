def format_dict_for_email(data_dict):
    """
    Takes a dictionary and formats it into a structured text for email.

    :param data_dict: Dictionary with unknown fields
    :return: Formatted string for email
    """
    if not isinstance(data_dict, dict):
        raise ValueError("Input must be a dictionary")

    formatted_text = ["<h2>Submission Details</h2>", "<ul>"]

    for key, value in data_dict.items():
        formatted_key = key.replace("_", " ").title()
        formatted_value = str(value).replace("\n", "<br>")
        formatted_text.append(
            f"<li><strong>{formatted_key}:</strong> {formatted_value}</li>"
        )

    formatted_text.append("</ul>")
    return "\n".join(formatted_text)
