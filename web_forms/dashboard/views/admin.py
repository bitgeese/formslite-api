from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from web_forms.access_keys.models import SimpleUser


@staff_member_required
def admin_panel(request):
    return render(request, "admin.html", {"users": SimpleUser.objects.all()})


