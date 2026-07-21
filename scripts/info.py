"""Info helper script for the project runner."""
import sys


def list_endpoints():
    from app.app import app

    count = 0
    for inc in app.routes:
        if type(inc).__name__ == "_IncludedRouter":
            router = inc.original_router
            prefix = getattr(router, "prefix", "")
            for r in router.routes:
                if hasattr(r, "methods"):
                    methods = ",".join(sorted(r.methods - {"HEAD", "OPTIONS"}))
                    print(f"  {methods:8s} {prefix}{r.path}")
                    count += 1
        elif hasattr(inc, "methods") and hasattr(inc, "path"):
            methods = ",".join(sorted(inc.methods - {"HEAD", "OPTIONS"}))
            print(f"  {methods:8s} {inc.path}")
            count += 1
    print(f"\n  Total: {count} endpoints")


def list_tables():
    # Import all entity modules to register tables with Base
    import importlib
    import pkgutil

    import app.modules

    for importer, modname, ispkg in pkgutil.walk_packages(
        app.modules.__path__, app.modules.__name__ + "."
    ):
        if "entities" in modname:
            try:
                importlib.import_module(modname)
            except Exception:
                pass

    from app.modules.shared.infrastructure.models import Base

    for t in sorted(Base.metadata.tables.keys()):
        print(f"  {t}")
    print(f"\n  Total: {len(Base.metadata.tables)} tables")


def list_modules():
    import os

    print(f"  {'Module':<45s} {'Files':>6s} {'Lines':>8s}")
    print(f"  {'-' * 45} {'-' * 6} {'-' * 8}")
    total_files = 0
    total_lines = 0
    for root, dirs, files in os.walk("app/modules"):
        if "__pycache__" in root:
            continue
        py_files = [f for f in files if f.endswith(".py")]
        if py_files:
            lines = 0
            for f in py_files:
                with open(os.path.join(root, f), "r", encoding="utf-8") as fh:
                    lines += sum(1 for _ in fh)
            name = root.replace("app\\modules\\", "").replace("app/modules/", "")
            if not name:
                name = "(root)"
            print(f"  {name:<45s} {len(py_files):>6d} {lines:>8d}")
            total_files += len(py_files)
            total_lines += lines
    print(f"  {'-' * 45} {'-' * 6} {'-' * 8}")
    print(f"  {'TOTAL':<45s} {total_files:>6d} {total_lines:>8d}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "endpoints"
    if cmd == "endpoints":
        list_endpoints()
    elif cmd == "tables":
        list_tables()
    elif cmd == "modules":
        list_modules()
    else:
        print(f"Unknown command: {cmd}")
