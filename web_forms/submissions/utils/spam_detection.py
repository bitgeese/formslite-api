HONEYPOT_FIELD = "honeycomb"


def is_honeypot_triggered(form_data):
    honeypot_field = form_data.pop(HONEYPOT_FIELD, None)
    if honeypot_field:
        return True


def is_spam(form_data):
    checks = [is_honeypot_triggered]
    if any(check(form_data) for check in checks):
        return True
