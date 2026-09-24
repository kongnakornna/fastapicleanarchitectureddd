"""llm SSE helper — Server-Sent Events streaming"""
from __future__ import annotations
import json
from typing import AsyncIterator

from fastapi.responses import StreamingResponse


def sse_response(stream: AsyncIterator[dict]) -> StreamingResponse:
    """TH: SSE response | EN: SSE streaming response"""

    async def event_gen() -> AsyncIterator[str]:
        try:
            async for chunk in stream:
                yield (
                    f"data: {json.dumps(chunk, default=str)}\n\n"
                )
            yield "data: [DONE]\n\n"
        except Exception as e:
            error = json.dumps({"error": str(e)})
            yield f"data: {error}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
