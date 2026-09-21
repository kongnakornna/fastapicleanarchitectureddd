from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from ..infrastructure.notification_client import NotificationClient


def _client(request):
    return NotificationClient(token=request.session.get("access_token"))


class NotificationListView(View):
    template_name = "notification/list.html"

    def get(self, request):
        return render(request, self.template_name, {
            "notifications": _client(request).list(),
        })


class NotificationDropdownView(View):
    """HTMX partial — แทน dropdown header."""
    template_name = "notification/_dropdown.html"

    def get(self, request):
        return render(request, self.template_name, {
            "notifications": _client(request).list(),
            "unread_count": _client(request).unread_count(),
        })


class MarkReadView(View):
    def post(self, request, pk):
        _client(request).mark_read(pk)
        if request.headers.get("HX-Request"):
            return HttpResponse(status=204)
        return redirect("notification:list")


class MarkAllReadView(View):
    def post(self, request):
        _client(request).mark_all_read()
        if request.headers.get("HX-Request"):
            return HttpResponse(status=204)
        return redirect("notification:list")
