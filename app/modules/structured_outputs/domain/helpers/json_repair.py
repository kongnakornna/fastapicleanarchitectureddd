"""json_repair — fallback extract + common fixes"""
from __future__ import annotations
import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

_CODE_FENCE = re.compile(r"```(?:json|JSON)?\s*(.*?)```", re.DOTALL)
_TRAILING_COMMA = re.compile(r",\s*([}\]])")


def extract_json(text: str) -> Optional[Any]:
    """TH: ดึง JSON จากข้อความ | EN: extract JSON from text"""
    if not text:
        return None
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    m = _CODE_FENCE.search(text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:
            pass

    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except Exception:
                continue
    return None


def repair_json(text: str) -> Optional[Any]:
    """TH: best-effort JSON repair | EN: best-effort JSON repair"""
    raw = extract_json(text)
    if raw is not None:
        return raw
    if not text:
        return None

    s = text.strip()
    s = _TRAILING_COMMA.sub(r"\1", s)
    s = re.sub(r"\bNaN\b", "null", s)
    s = re.sub(r"\bInfinity\b", "null", s)

    if s and s[0] not in "{[\"":
        m = re.search(r"([{\[].*[}\]])", s, re.DOTALL)
        if m:
            s = m.group(1)

    try:
        return json.loads(s)
    except Exception:
        pass

    try:
        fixed = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", r'"\1":', s)
        return json.loads(fixed)
    except Exception:
        pass

    logger.debug("json repair failed for: %s", text[:120])
    return None
