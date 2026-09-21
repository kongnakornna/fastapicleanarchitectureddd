import httpx
from django.conf import settings
from django.http import JsonResponse
from django.views import View


class HealthView(View):
    def get(self, request):
        status = {"django": "ok", "fastapi": "unknown"}
        try:
            with httpx.Client(timeout=2) as c:
                r = c.get(f"{settings.FASTAPI_BASE_URL.rstrip('/')}/health")
                status["fastapi"] = "ok" if r.status_code == 200 else f"http {r.status_code}"
        except Exception as e:
            status["fastapi"] = f"error: {type(e).__name__}"
        return JsonResponse(status)
