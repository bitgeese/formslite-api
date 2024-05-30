from rest_framework.throttling import AnonRateThrottle


class AccessKeyCreateRateThrottle(AnonRateThrottle):
    scope = "access_key"


class SubmissionRateThrottle(AnonRateThrottle):
    scope = "submission"
