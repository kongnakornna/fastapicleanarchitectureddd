from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse


def login_required_fastapi(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("access_token"):
            return redirect(f"{reverse('auth:login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper
