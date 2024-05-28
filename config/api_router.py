from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from web_forms.access_keys.api.views import AccessKeyViewSet
from web_forms.submissions.api.views import SubmissionViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("access_keys", AccessKeyViewSet)
router.register("submissions", SubmissionViewSet)


app_name = "api"
urlpatterns = router.urls
