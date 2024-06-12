import logging

import requests
from django.conf import settings

HONEYPOT_FIELD = "honeycomb"

logger = logging.getLogger(__name__)


def is_honeypot_triggered(form_data):
    honeypot_field = form_data.pop(HONEYPOT_FIELD, None)
    if honeypot_field:
        logger.info("Honeypot field triggered.")
        return True
    return False


def is_spam_ip(request, threshold=50):
    if not settings.ABUSEIPDB_KEY:
        logger.warning("ABUSEIPDB_KEY is not set in settings.")
        return True
    ip_address = request.META.get("REMOTE_ADDR")
    logger.info("Checking IP address %s for spam.", ip_address)
    url = "https://api.abuseipdb.com/api/v2/check"
    querystring = {"ipAddress": ip_address, "maxAgeInDays": "90"}
    headers = {
        "Accept": "application/json",
        "Key": settings.ABUSEIPDB_KEY,
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        result = response.json()
        abuse_confidence_score = result["data"]["abuseConfidenceScore"]
        logger.info(
            "Abuse confidence score for IP %s: %d", ip_address, abuse_confidence_score
        )
        return abuse_confidence_score >= threshold
    except requests.RequestException as e:
        logger.exception("Error checking IP address %s: %s", ip_address, e)
        return False


def is_spam(form_data, request):
    logger.info("Checking submission for spam.")
    checks = [(form_data, is_honeypot_triggered), (request, is_spam_ip)]
    if any(check(arg) for arg, check in checks):
        logger.info("Submission detected as spam.")
        return True
    logger.info("Submission is not spam.")
    return False
