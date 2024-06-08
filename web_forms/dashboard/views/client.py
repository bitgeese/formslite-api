from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from web_forms.access_keys.models import SimpleUser, UserSettings

from ..forms import AutoRespondSettingsForm, MagicSignInForm, NotionLinkForm
from ..magic_links import decode_uid, get_user_by_uid, send_sign_in_email


def verify_email(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """
    Verify user email after the user clicks on the email link.
    """
    uid = decode_uid(uidb64)
    user = get_user_by_uid(uid) if uid else None

    if user and default_token_generator.check_token(user, token):
        user.has_verified_email = True
        user.save()
        login(request, user)
        return redirect("dashboard:home")

    print("Email verification failed")
    return redirect("dashboard:sign_in")


class SendSignInEmail(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_anonymous and request.user.has_verified_email:
            return redirect("dashboard:home")
        form = MagicSignInForm()
        return render(request, "login.html", {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        email = request.POST["email"]
        try:
            user = SimpleUser.objects.get(email=email)
            if not user.is_paid:
                return redirect("https://formslite.io/pricing")
        except SimpleUser.DoesNotExist:
            return render(
                request,
                "login.html",
                {"form": MagicSignInForm(), "error": "user does not exist"},
            )
        return self._send_verification_and_respond(user)

    @staticmethod
    def _send_verification_and_respond(user: SimpleUser) -> HttpResponse:
        send_sign_in_email(user)
        message = (
            f"We sent your ⚡️FormsLite.io login link to "
            f'<a href=mailto:{user.email}" target="_blank">{user.email}</a> '
            "Please check your email to login"
        )
        return HttpResponse(message)


def home(request: HttpRequest) -> HttpResponse:
    if not request.user.is_anonymous and request.user.has_verified_email:
        form_1_success, form_2_success = "", ""
        settings_instance = get_object_or_404(UserSettings, user=request.user)
        if request.method == "POST":
            print("POST:", request.POST)
            form1 = AutoRespondSettingsForm(request.POST, instance=settings_instance)
            if form1.is_valid():
                form1.save()
                form_1_success = "Settings updated"
            form2 = NotionLinkForm(request.POST)
            if form2.is_valid():
                instance = form2.save(commit=False)
                instance.user = request.user
                instance.save()
                form_2_success = "Link Added"

        else:
            form1 = AutoRespondSettingsForm(instance=settings_instance)
            form2 = NotionLinkForm()

        return render(
            request,
            "home.html",
            {
                "form1": form1,
                "form1_success": form_1_success,
                "form2": form2,
                "form2_success": form_2_success,
                "databases": request.user.notion_client.get_all_databases(),
                "access_keys": request.user.keys.all(),
                "notion_links": request.user.notion_links.all(),
            },
        )
    else:
        return redirect("dashboard:sign_in")


def add_notion_link(request):
    if request.method == "POST":
        form = NotionLinkForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            print(instance)
            return redirect("dashboard:home")
        else:
            return form.errors


def logout(request: HttpRequest) -> HttpResponse:
    request.session.flush()
    return redirect("dashboard:sign_in")
