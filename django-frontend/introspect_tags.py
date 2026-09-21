import inspect
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
print("arg0:", sys.argv[0], flush=True)
print("DJANGO_SETTINGS_MODULE env:", os.environ.get("DJANGO_SETTINGS_MODULE"), flush=True)
print("sys.path[0:6]:", sys.path[:6], flush=True)

import platform

print("python:", platform.python_version(), flush=True)

step("django.setup()")
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
print("django " + django.get_version(), flush=True)
print("django file:", django.__file__, flush=True)

from django.conf import settings

step("settings")
print("SETTINGS_MODULE:", getattr(settings, "SETTINGS_MODULE", None), flush=True)
print("INSTALLED_APPS:", settings.INSTALLED_APPS, flush=True)
print("TEMPLATES:", settings.TEMPLATES, flush=True)

step("templatetags package presence")
for path in [
    "apps/shared/presentation/templatetags/__init__.py",
    "apps/shared/presentation/__init__.py",
    "apps/shared/presentation/apps.py",
]:
    print(f"{path}: exists={os.path.exists(path)}", flush=True)

step("get_installed_libraries()")
from django.template.backends.django import get_installed_libraries

inst = sorted(get_installed_libraries().keys())
print("installed:", inst, flush=True)
print("has icons:", "icons" in inst, flush=True)

step("get_library per name")
from django.template import loader

for name in ("icons", "static", "i18n"):
    try:
        lib = loader.get_library(name)
        print(f"{name}: tags={sorted(lib.tags)} filters={sorted(lib.filters)}", flush=True)
    except Exception:
        print(f"{name}: FAILED", flush=True)
        traceback.print_exc()

step("engine introspection")
from django.template import engines

engine = engines["django"]
print("template_libraries:", sorted(engine.template_libraries), flush=True)
print("template_builtins:", [getattr(b, "name", None) for b in engine.template_builtins], flush=True)

step("minimal repros via Template(str)")
from django.template import Context, Template

wrap(
    "icons alone + icon tag",
    lambda: Template('{% load icons %}{% icon "palette" %}', engine=engine).render(Context({})),
)
wrap(
    "static+i18n load only",
    lambda: Template("{% load static i18n %}OK", engine=engine).render(Context({})),
)
wrap(
    "static+i18n+icons load only",
    lambda: Template("{% load static i18n icons %}OK", engine=engine).render(Context({})),
)
wrap(
    "full header + icon tag",
    lambda: Template('{% load static i18n icons %}{% icon "palette" %}', engine=engine).render(Context({})),
)

AUTH_PATH = "apps/authentication/presentation/templates/auth/auth_layout.html"

step("read auth_layout.html")
with open(AUTH_PATH, encoding="utf-8") as f:
    src = f.read()
lines = src.splitlines()
print("chars:", len(src), " BOM:", src.startswith("\ufeff"), flush=True)
for i, ln in enumerate(lines[:3], start=1):
    print(f"line {i}: {ln!r}", flush=True)
print("line 45:", repr(lines[44]) if len(lines) >= 45 else "MISSING", flush=True)

step("lexer first 14 tokens")
from django.template.base import Lexer

tokens = Lexer(src, origin=None).tokenize()
for i, tok in enumerate(tokens[:14]):
    print(f"tok {i}: type={tok.token_type} line={tok.lineno} contents={tok.contents[:70]!r}", flush=True)

step("snapshot-parser full parse of auth_layout.html")
from django.template.base import Parser as BaseParser


class SnapshotParser(BaseParser):
    def next_token(self):
        tok = super().next_token()
        self.history.append((tok.lineno, tok.token_type, tok.contents[:60]))
        return tok


sp = SnapshotParser(tokens, libraries=engine.template_libraries, builtins=engine.template_builtins, origin=None)
sp.history = []
try:
    nodelist = sp.parse()
    print("parse OK, tags:", sorted(sp.tags), flush=True)
except Exception as ex:
    print("parse FAILED:", type(ex).__name__, ex, flush=True)
    print("tags at failure:", sorted(sp.tags), flush=True)
    print("icon in tags:", "icon" in sp.tags, flush=True)
    print("history tail:", sp.history[-8:], flush=True)

step("head-only parser (first 4 tokens) tags after")
from django.template.base import Parser

hp = Parser(tokens[:4], libraries=engine.template_libraries, builtins=engine.template_builtins, origin=None)
try:
    hp.parse()
    print("head tags:", sorted(hp.tags), flush=True)
except Exception as ex:
    print("head parse FAILED:", type(ex).__name__, ex, flush=True)
    print("head tags part:", sorted(hp.tags), flush=True)

step("get_template resolution")
try:
    t = engine.get_template("auth/auth_layout.html")
    print("origin:", t.origin, flush=True)
except Exception:
    traceback.print_exc()

step("django internals around parser")
from django.template import base as base_mod

print("base.py:", base_mod.__file__, flush=True)
try:
    print("--- Parser.parse source ---", flush=True)
    print(inspect.getsource(base_mod.Parser.parse), flush=True)
except Exception as ex:
    print("no parse source:", ex, flush=True)
try:
    print("--- Parser.load_command source ---", flush=True)
    print(inspect.getsource(base_mod.Parser.load_command), flush=True)
except Exception as ex:
    print("no load_command:", ex, flush=True)
blines = open(base_mod.__file__, encoding="utf-8").read().splitlines()
for i in range(486, 522):
    if 0 <= i < len(blines):
        print(f"{i+1}: {blines[i]}", flush=True)

print("\n== DONE ==", flush=True)
