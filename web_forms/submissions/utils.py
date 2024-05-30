from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html


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


def send_submission_email(access_key, data):
    subject = "New Submission Received"
    text_content = (
        "A new submission has been received. "
        "Here are the details:\n\nAccess Key: {}\n\n{}".format(
            access_key.id, format_dict_for_email(data)
        )
    )
    html_content = format_html(
        "<p>A new submission has been received.</p>"
        "<p>Here are the details:</p>"
        "<p>Access Key: {}</p>"
        "<div>{}</div>".format(access_key.id, format_dict_for_email(data))
    )

    recipient_list = [access_key.email]

    msg = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, recipient_list
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
