from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status, WebSocket
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.security import authenticate_websocket, no_authentication
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.websocket.application.exceptions import WebSocketException
from app.modules.websocket.application.mappers import connect_entity_mapper
from app.modules.websocket.application.use_cases import WebSocketUseCases
from app.modules.websocket.presentation.dependencies import get_websocket_use_cases
from app.modules.websocket.presentation.docs import connect_ws_docs, router_docs

router = APIRouter(**router_docs)

# TH: override status_code ใน docs dict (กัน kwargs ซ้ำ)
# EN: override status_code inside the docs dict (avoids duplicate kwarg)
_connect_ws_docs_426 = {
    **connect_ws_docs,
    "status_code": status.HTTP_426_UPGRADE_REQUIRED,
}


# ═════════════════════════════════════════════════════════════════
# GET — Reference only
# ═════════════════════════════════════════════════════════════════
@router.get("/connect/", **_connect_ws_docs_426)
@router.get(
    "/connect",
    include_in_schema=False,
    status_code=status.HTTP_426_UPGRADE_REQUIRED,
)
async def websocket_connect_reference(
    _: Annotated[None, Depends(no_authentication)],
) -> JSONResponse:
    """
    TH: reference endpoint — ต้องใช้ WebSocket protocol
        ลบ "code" ออกจาก content เพราะ middleware ใส่ให้เอง
    EN: reference endpoint — must use WebSocket protocol.
        Do NOT include "code" in content — middleware adds it.
    """
    return JSONResponse(
        status_code=status.HTTP_426_UPGRADE_REQUIRED,
        content={
            # TH: ไม่ใส่ "code" ที่นี่ — middleware จะใส่ให้เอง
            # EN: no "code" here — middleware adds it
            "message": "Upgrade Required",
            "data": {
                "errors": "This endpoint requires the WebSocket protocol.",
                "errors_th": "endpoint นี้ต้องใช้ WebSocket protocol",
                "hint": (
                    "Connect with "
                    "ws://localhost:8000/api/v1/websocket/connect/"
                ),
            },
        },
        headers={"Upgrade": "websocket", "Connection": "Upgrade"},
    )


# ═════════════════════════════════════════════════════════════════
# WebSocket — real endpoint
# ═════════════════════════════════════════════════════════════════
@router.websocket("/connect/")
@router.websocket("/connect")
async def websocket_connect(
    websocket: WebSocket,
    authentication: Annotated[Authentication, Depends(authenticate_websocket)],
    use_case: Annotated[WebSocketUseCases, Depends(get_websocket_use_cases)],
) -> None:
    """TH: WebSocket connect | EN: WebSocket connect"""
    try:
        connection = connect_entity_mapper(authentication)
        await use_case.connect(websocket, connection)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred in the websocket connect endpoint."
        )
        raise WebSocketException()
