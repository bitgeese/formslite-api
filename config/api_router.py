from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from web_forms.access_keys.api.views import AccessKeyViewSet
from web_forms.submissions.api.views import submission_view

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("access_keys", AccessKeyViewSet)


app_name = "api"
urlpatterns = router.urls
urlpatterns += [path("submission/", submission_view, name="submission")]
