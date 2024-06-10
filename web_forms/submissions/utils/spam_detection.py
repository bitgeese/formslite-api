import requests
from django.conf import settings

HONEYPOT_FIELD = "honeycomb"


def is_honeypot_triggered(form_data):
    honeypot_field = form_data.pop(HONEYPOT_FIELD, None)
    if honeypot_field:
        return True
    return False


def is_spam_ip(request, threshold=50):
    if not settings.ABUSEIPDB_KEY:
        return True
    ip_address = request.META.get("REMOTE_ADDR")
    url = "https://api.abuseipdb.com/api/v2/check"
    querystring = {"ipAddress": ip_address, "maxAgeInDays": "90"}
    headers = {
        "Accept": "application/json",
        "Key": settings.ABUSEIPDB_KEY,
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        result = response.json()
        abuse_confidence_score = result["data"]["abuseConfidenceScore"]
        return abuse_confidence_score >= threshold
    return False


def is_spam(form_data, request):
    checks = [(form_data, is_honeypot_triggered), (request, is_spam_ip)]
    if any(check(arg) for arg, check in checks):
        return True
