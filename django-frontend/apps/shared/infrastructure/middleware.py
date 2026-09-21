from django.shortcuts import redirect
from django.urls import reverse


class FastAPISessionMiddleware:
    """Redirect to login if FastAPI session token is missing on protected paths."""

    PUBLIC_PREFIXES = (
        "/auth/",
        "/admin/",
        "/static/",
        "/media/",
        "/i18n/",
        "/favicon.ico",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.access_token = request.session.get("access_token")
        request.refresh_token = request.session.get("refresh_token")

        if any(request.path.startswith(p) for p in self.PUBLIC_PREFIXES):
            return self.get_response(request)

        if not request.access_token:
            login_url = reverse("auth:login")
            return redirect(f"{login_url}?next={request.path}")

        return self.get_response(request)
