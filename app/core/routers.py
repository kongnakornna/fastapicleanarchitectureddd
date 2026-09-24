# app/core/routers.py - auto-register module routers
import importlib
from pathlib import Path

from fastapi import FastAPI

from app.core.logging import logger


def register_routers(app: FastAPI) -> None:
    """Auto-discover and register all module routers."""
    modules_dir = Path(__file__).parent.parent / "modules"
    if not modules_dir.exists():
        logger.warning("modules.dir.not.found", path=str(modules_dir))
        return

    registered: list[str] = []
    for mod_dir in sorted(modules_dir.iterdir()):
        if not mod_dir.is_dir() or mod_dir.name.startswith("_"):
            continue
        router_module = f"app.modules.{mod_dir.name}.presentation.routers"
        try:
            mod = importlib.import_module(router_module)
            router = getattr(mod, "router", None)
            if router is not None:
                app.include_router(router)
                registered.append(mod_dir.name)
        except ModuleNotFoundError:
            logger.debug("router.skip", module=mod_dir.name)
        except Exception as e:
            logger.warning("router.load.failed", module=mod_dir.name, error=str(e))

    logger.info("routers.registered", count=len(registered), modules=registered)
