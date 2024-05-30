HONEYPOT_FIELD = "topyenoh"


def is_honeypot_triggered(form_data):
    honeypot_field = form_data.get(HONEYPOT_FIELD)
    if honeypot_field:
        return True


def is_spam(form_data):
    checks = [is_honeypot_triggered]
    if any(check(form_data) for check in checks):
        return True
