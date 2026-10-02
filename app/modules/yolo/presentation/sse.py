"""SSE helper"""
from __future__ import annotations
import json
from typing import Any, AsyncIterator


async def sse_stream(source: AsyncIterator[Any]) -> AsyncIterator[str]:
    try:
        async for chunk in source:
            payload = json.dumps(chunk, default=str, ensure_ascii=False)
            yield f"data: {payload}\n\n"
    except Exception as e:
        err_payload = json.dumps({"error": str(e)})
        yield f"data: {err_payload}\n\n"
    finally:
        yield "data: [DONE]\n\n"
