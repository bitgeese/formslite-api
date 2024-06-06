from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.html import format_html

from web_forms.submissions.utils.spam_detection import HONEYPOT_FIELD

SKIP_FIELDS = [
    "redirect",
    "access_key",
    "from_name",
    "reply_to",
    HONEYPOT_FIELD,
]


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
        if key.lower() in SKIP_FIELDS:
            continue
        formatted_key = key.replace("_", " ").title()
        formatted_value = str(value).replace("\n", "<br>")
        formatted_text.append(
            f"<li><strong>{formatted_key}:</strong> {formatted_value}</li>"
        )

    formatted_text.append("</ul>")
    return "\n".join(formatted_text)


def send_submission_email(access_key, data):
    if "subject" in data:
        subject = data["subject"]
    else:
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

    recipient_list = [access_key.user.email]

    from_email = settings.DEFAULT_FROM_EMAIL
    from_name = data.get("from_name")
    if from_name:
        from_email = f"{from_name} <{settings.DEFAULT_FROM_EMAIL_ADDR}>"

    reply_to = [data.get("reply_to")] if data.get("reply_to") else None

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, recipient_list, reply_to=reply_to
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def send_usage_limit_reached_email(access_key):
    subject = "Usage Limit Reached"
    message = (
        f"Access Key: {access_key.id} ({access_key.user.email}) reached usage limit, "
    )
    "wait until the end of the month for it to reset, or upgrade your access key"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [admin[1] for admin in settings.ADMINS] + [access_key.user.email]
    send_mail(subject, message, from_email, recipient_list)
