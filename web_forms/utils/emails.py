from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.html import format_html

from web_forms.submissions.utils.spam_detection import HONEYPOT_FIELD

SKIP_FIELDS = [
    "redirect",
    "access_key",
    "from_name",
    "reply_to",
    "cc_emails",
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


def send_submission_email(access_key, validated_data):
    data = validated_data["data"]
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
    from_name = validated_data.get("from_name")
    if from_name:
        from_email = f"{from_name} <{settings.DEFAULT_FROM_EMAIL_ADDR}>"

    reply_to = (
        [validated_data.get("reply_to")] if validated_data.get("reply_to") else None
    )

    cc_emails = validated_data.get("cc_emails", [])
    print("DUPA:", cc_emails)

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        recipient_list,
        reply_to=reply_to,
        cc=cc_emails,
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


def send_auto_respond(submission_data):
    from_email = settings.DEFAULT_FROM_EMAIL
    from_name = ""
    if from_name:
        from_email = f"{from_name} <{settings.DEFAULT_FROM_EMAIL_ADDR}>"

    intro_text = ""
    show_submission_copy = True
    text_content = (
        f"{intro_text}\n"
        f"{format_dict_for_email(submission_data) if show_submission_copy else ''}"
    )

    html_content = format_html(
        "<p>{}</p>"
        "<div>{}</div>".format(
            intro_text,
            format_dict_for_email(submission_data) if show_submission_copy else "",
        )
    )

    subject = "sample text"
    submission_email = ""

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        [submission_email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
