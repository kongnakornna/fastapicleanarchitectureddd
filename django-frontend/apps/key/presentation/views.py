from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from ..infrastructure.key_client import KeyClient


def _client(request):
    return KeyClient(token=request.session.get("access_token"))


class KeyListView(View):
    template_name = "key/list.html"

    def get(self, request):
        return render(request, self.template_name, {
            "keys": _client(request).list_keys(),
        })


class KeyCreateView(View):
    template_name = "key/form.html"

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        name = request.POST.get("name", "").strip()
        if not name:
            return render(request, self.template_name, {"error": "Name required"}, status=422)
        result = _client(request).create_key(name)
        messages.success(request, f"Key created: {result.get('key', '')}")
        return render(request, self.template_name, {"new_key": result.get("key")})


class KeyDetailView(View):
    template_name = "key/detail.html"

    def get(self, request, pk):
        return render(request, self.template_name, {"key": _client(request).get_key(pk)})


class KeyRevokeView(View):
    def post(self, request, pk):
        _client(request).revoke_key(pk)
        messages.success(request, "Key revoked.")
        return redirect("key:list")
