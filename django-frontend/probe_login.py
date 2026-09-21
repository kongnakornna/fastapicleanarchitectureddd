import os
import sys
import traceback

STEP = 0


def step(name):
    global STEP
    STEP += 1
    print(f"\n=== STEP {STEP}: {name} ===", flush=True)


def wrap(name, fn):
    step(name)
    try:
        result = fn()
        print(f"-- OK: {result}", flush=True)
        return result
    except Exception:
        print("-- FAILED (traceback below)", flush=True)
        traceback.print_exc()
        return None


step("env / cwd / sys.path")
print("cwd:", os.getcwd(), flush=True)
print("DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"), flush=True)
print("sys.path[0:5]:", sys.path[:5], flush=True)

wrap(
    "django.setup()",
    lambda: (lambda dj: (dj.setup(), "django " + dj.get_version()))(
        __import__("django")
    ),
)

app_configs = wrap(
    "app configs",
    lambda: [f"{c.name}:{c.path}" for c in __import__("django").apps.get_app_configs()],
)

installed_libraries = wrap(
    "get_installed_libraries()",
    lambda: sorted(
        __import__("django").template.loader.get_installed_libraries().keys()
    ),
)

templatetag_libraries = wrap(
    "engines['django'].get_templatetag_libraries({})",
    lambda: sorted(
        __import__("django").template.engines["django"]
        .get_templatetag_libraries({})
        .keys()
    ),
)


def lib_has_icon():
    libs = __import__("django").template.engines["django"].get_templatetag_libraries({})
    hits = {name: ("icon" in lib.tags) for name, lib in libs.items()}
    return {k: v for k, v in hits.items() if v}


wrap("libs exposing an 'icon' tag", lib_has_icon)


def direct_icons():
    import icons

    return (
        f"icons.__file__={icons.__file__} | tags={sorted(icons.register.tags)} "
        f"| 'palette' in ICONS={('palette' in icons.ICONS)}"
    )


wrap("direct import icons (register.tags / ICONS)", direct_icons)

wrap(
    "render_to_string('auth/auth_layout.html')",
    lambda: __import__("django").template.loader.render_to_string("auth/auth_layout.html"),
)

wrap(
    "render_to_string('auth/login.html')",
    lambda: __import__("django").template.loader.render_to_string("auth/login.html"),
)


def client_get_login():
    from django.test import Client

    resp = Client(HTTP_HOST="localhost").get("/auth/login/")
    return f"status={resp.status_code} len={len(resp.content)}"


wrap(r"Client(HTTP_HOST='localhost').get('/auth/login/')", client_get_login)

print("\n=== PROBE DONE ===", flush=True)
