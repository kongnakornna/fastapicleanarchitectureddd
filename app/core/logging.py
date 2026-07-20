import sys
from pathlib import Path

import orjson
import stackprinter
from loguru import logger
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.data import JsonLexer

from app.core.settings import settings

lexer = JsonLexer()
formatter = Terminal256Formatter(style=settings.LOGS_PYGMENTS_STYLE)
orjson_options = orjson.OPT_NAIVE_UTC
if settings.APPLICATION_ENVIRONMENT_DEBUG:
    orjson_options |= orjson.OPT_INDENT_2

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


def serialize(record: dict) -> str:
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "source": f"{record['file'].name}:{record['function']}:{record['line']}",
    }
    subset.update(record["extra"])
    if record["exception"]:
        subset["exception"] = stackprinter.format(record["exception"])
    formatted_json = orjson.dumps(subset, default=str, option=orjson_options).decode()
    if settings.APPLICATION_ENVIRONMENT_DEBUG:
        formatted_json = highlight(formatted_json, lexer, formatter)
    return formatted_json


def serialize_plain(record: dict) -> str:
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "source": f"{record['file'].name}:{record['function']}:{record['line']}",
    }
    subset.update(record["extra"])
    if record["exception"]:
        subset["exception"] = stackprinter.format(record["exception"])
    return orjson.dumps(subset, default=str, option=orjson_options).decode()


def init_loguru() -> None:
    logger.remove()
    logger.add(lambda message: print(serialize(message.record), file=sys.stderr))  # type: ignore
    logger.add(
        LOGS_DIR / "app_{time:YYYY-MM-DD}.log",
        format="{message}",
        serialize=False,
        rotation="00:00",
        retention="30 days",
        compression="zip",
        level="DEBUG",
        backtrace=True,
        diagnose=True,
    )
