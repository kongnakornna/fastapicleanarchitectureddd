"""llm HTTP routers"""
from __future__ import annotations
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.modules.llm.application.use_case import LLMUseCase
from app.modules.llm.domain.exceptions import (
    ConversationNotFoundError, LLMError,
    ModelNotFoundError, RateLimitExceededError,
)
from app.modules.llm.domain.value_objects import ChatOptions
from app.modules.llm.presentation.dependencies import get_llm_use_case
from app.modules.llm.presentation.docs import (
    RESPONSE_CHAT_200, RESPONSE_ERROR_400, RESPONSE_ERROR_402,
    RESPONSE_ERROR_404, RESPONSE_ERROR_429, RESPONSE_ERROR_502,
)
from app.modules.llm.presentation.schemas import (
    ChatRequest, ChatResponse, CompletionRequest,
    ConversationCreateRequest, ConversationDetailResponse,
    ConversationResponse, ModelResponse, ProviderResponse,
    UsageResponse,
)
from app.modules.llm.presentation.sse import sse_response

router = APIRouter(prefix="/llm", tags=["LLM"])


def _error_status(exc: Exception) -> int:
    if isinstance(exc, ModelNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, ConversationNotFoundError):
        return status.HTTP_404_NOT_FOUND
    if isinstance(exc, RateLimitExceededError):
        return status.HTTP_429_TOO_MANY_REQUESTS
    return status.HTTP_400_BAD_REQUEST


class _CtxStub:
    def __init__(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID,
    ) -> None:
        self.tenant_id = tenant_id
        self.user_id = user_id


async def _get_ctx() -> Any:
    try:
        from app.core.context import get_context
        return await get_context()
    except Exception:
        return _CtxStub(
            tenant_id=uuid.UUID(int=1),
            user_id=uuid.UUID(int=2),
        )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat completion (sync)",
    operation_id="llm_chat",
    responses={
        200: RESPONSE_CHAT_200,
        400: RESPONSE_ERROR_400,
        402: RESPONSE_ERROR_402,
        404: RESPONSE_ERROR_404,
        429: RESPONSE_ERROR_429,
        502: RESPONSE_ERROR_502,
    },
)
async def chat(
    payload: ChatRequest,
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
    idem_key: Annotated[
        str, Header(alias="Idempotency-Key", min_length=8),
    ] = "",
) -> ChatResponse:
    """TH: chat completion | EN: chat completion"""
    ctx = await _get_ctx()
    try:
        options = ChatOptions(
            temperature=payload.temperature,
            top_p=payload.top_p,
            max_tokens=payload.max_tokens,
        )
        conv_id = (
            uuid.UUID(payload.conversation_id)
            if payload.conversation_id else None
        )
        result = await uc.chat(
            ctx=ctx, conversation_id=conv_id,
            model_name=payload.model,
            user_message=payload.message,
            options=options,
            system_prompt=payload.system_prompt,
            idempotency_key=idem_key,
        )
        return ChatResponse(**result)
    except LLMError as e:
        raise HTTPException(
            _error_status(e), detail=str(e),
        ) from e


@router.post(
    "/chat/stream",
    summary="Chat completion (SSE stream)",
    operation_id="llm_chat_stream",
)
async def chat_stream(
    payload: ChatRequest,
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
) -> Any:
    """TH: chat streaming | EN: chat streaming (SSE)"""
    ctx = await _get_ctx()
    options = ChatOptions(
        temperature=payload.temperature,
        top_p=payload.top_p,
        max_tokens=payload.max_tokens,
        stream=True,
    )
    conv_id = (
        uuid.UUID(payload.conversation_id)
        if payload.conversation_id else None
    )
    stream = uc.chat_stream(
        ctx=ctx, conversation_id=conv_id,
        model_name=payload.model,
        user_message=payload.message,
        options=options,
        system_prompt=payload.system_prompt,
    )
    return sse_response(stream)


@router.post(
    "/completions",
    response_model=ChatResponse,
    summary="Raw completion",
    operation_id="llm_completion",
)
async def completions(
    payload: CompletionRequest,
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
) -> ChatResponse:
    """TH: raw completion | EN: raw completion"""
    ctx = await _get_ctx()
    options = ChatOptions(
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    try:
        result = await uc.chat(
            ctx=ctx, conversation_id=None,
            model_name=payload.model,
            user_message=payload.prompt,
            options=options,
        )
        return ChatResponse(**result)
    except LLMError as e:
        raise HTTPException(
            _error_status(e), detail=str(e),
        ) from e


@router.get(
    "/conversations",
    response_model=list[ConversationResponse],
    summary="List conversations",
    operation_id="llm_list_conversations",
)
async def list_conversations(
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
    limit: int = 50,
) -> list[ConversationResponse]:
    ctx = await _get_ctx()
    rows = await uc.list_conversations(ctx, limit)
    return [ConversationResponse(**r) for r in rows]


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create conversation",
    operation_id="llm_create_conversation",
)
async def create_conversation(
    payload: ConversationCreateRequest,
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
) -> ConversationResponse:
    ctx = await _get_ctx()
    try:
        result = await uc.create_conversation(
            ctx, payload.model, payload.title,
        )
        return ConversationResponse(**result)
    except LLMError as e:
        raise HTTPException(
            _error_status(e), detail=str(e),
        ) from e


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Get conversation",
    operation_id="llm_get_conversation",
)
async def get_conversation(
    conversation_id: uuid.UUID,
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
) -> ConversationDetailResponse:
    ctx = await _get_ctx()
    try:
        result = await uc.get_conversation(ctx, conversation_id)
        return ConversationDetailResponse(**result)
    except LLMError as e:
        raise HTTPException(
            _error_status(e), detail=str(e),
        ) from e


@router.get(
    "/providers",
    response_model=list[ProviderResponse],
    summary="List providers",
    operation_id="llm_list_providers",
)
async def list_providers(
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
) -> list[ProviderResponse]:
    ctx = await _get_ctx()
    rows = await uc.list_providers(ctx)
    return [ProviderResponse(**r) for r in rows]


@router.get(
    "/models",
    response_model=list[ModelResponse],
    summary="List models",
    operation_id="llm_list_models",
)
async def list_models(
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
) -> list[ModelResponse]:
    ctx = await _get_ctx()
    rows = await uc.list_models(ctx)
    return [ModelResponse(**r) for r in rows]


@router.get(
    "/usage",
    response_model=UsageResponse,
    summary="Usage stats (tenant + user)",
    operation_id="llm_usage",
)
async def get_usage(
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
    days: int = 30,
) -> UsageResponse:
    ctx = await _get_ctx()
    result = await uc.get_usage(ctx, days)
    return UsageResponse(**result)


@router.get(
    "/usage/me",
    response_model=UsageResponse,
    summary="Usage stats (user)",
    operation_id="llm_usage_me",
)
async def get_usage_me(
    uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
    days: int = 30,
) -> UsageResponse:
    ctx = await _get_ctx()
    result = await uc.get_usage(ctx, days)
    return UsageResponse(**result)
