"""langchain HTTP router"""
from __future__ import annotations
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.langchain.application.exceptions import AppError
from app.modules.langchain.application.use_case import LangChainUseCase
from app.modules.langchain.domain.exceptions import LCError
from app.modules.langchain.domain.value_objects import (
    AgentSpec, ChainSpec,
)
from app.modules.langchain.presentation.dependencies import (
    Ctx, get_ctx, get_use_case,
)
from app.modules.langchain.presentation.schemas import (
    AgentCreateRequest, AgentOut, ChainCreateRequest, ChainOut,
    InvokeRequest, InvokeResponse, MemoryOut, MemoryUpdateRequest,
    RunOut, TraceOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lc", tags=["LangChain"])


def _raise(exc: Exception) -> None:
    if isinstance(exc, LCError):
        http = 400
        code = getattr(exc, "code", "DOMAIN_ERROR")
        if code == "NOT_FOUND":
            http = 404
        elif code == "VALIDATION_ERROR":
            http = 422
        elif code == "CONFLICT":
            http = 409
        elif code == "LIMIT_EXCEEDED":
            http = 402
        elif code == "PROVIDER_ERROR":
            http = 502
        raise HTTPException(
            status_code=http,
            detail={"code": code, "message": str(exc)},
        )
    if isinstance(exc, AppError):
        raise HTTPException(
            status_code=getattr(exc, "http_status", 400),
            detail={
                "code": getattr(exc, "code", "APP_ERROR"),
                "message": str(exc),
            },
        )
    logger.exception("unhandled error")
    raise HTTPException(
        status_code=500,
        detail={"code": "INTERNAL_ERROR", "message": "internal error"},
    )


@router.get("/chains", response_model=list[ChainOut])
async def list_chains(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> list[ChainOut]:
    try:
        items = await uc.list_chains(ctx)
        return [ChainOut.model_validate(c.model_dump()) for c in items]
    except (LCError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/chains", response_model=ChainOut, status_code=201)
async def create_chain(
    req: ChainCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> ChainOut:
    try:
        spec = ChainSpec(
            name=req.name, chain_type=req.chain_type,
            config=req.config, description=req.description,
            version=req.version,
        )
        row = await uc.register_chain(ctx, spec)
        return ChainOut.model_validate(row.model_dump())
    except (LCError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/chains/{chain_id}/invoke", response_model=InvokeResponse)
async def invoke_chain(
    chain_id: uuid.UUID,
    req: InvokeRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> InvokeResponse:
    try:
        out = await uc.invoke_chain(ctx, chain_id=chain_id,
                                    inputs=req.inputs)
        return InvokeResponse(**out)
    except (LCError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/agents", response_model=list[AgentOut])
async def list_agents(
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> list[AgentOut]:
    try:
        items = await uc.list_agents(ctx)
        return [AgentOut.model_validate(a.model_dump()) for a in items]
    except (LCError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/agents", response_model=AgentOut, status_code=201)
async def create_agent(
    req: AgentCreateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> AgentOut:
    try:
        spec = AgentSpec(
            name=req.name, agent_type=req.agent_type,
            tools=req.tools, model=req.model,
            max_iterations=req.max_iterations,
            system_prompt=req.system_prompt,
            config=req.config,
        )
        row = await uc.register_agent(ctx, spec)
        return AgentOut.model_validate(row.model_dump())
    except (LCError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/agents/{agent_id}/invoke", response_model=InvokeResponse)
async def invoke_agent(
    agent_id: uuid.UUID,
    req: InvokeRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> InvokeResponse:
    try:
        question = req.question or str(req.inputs.get("input", ""))
        out = await uc.invoke_agent(
            ctx, agent_id=agent_id, question=question,
        )
        return InvokeResponse(**out)
    except (LCError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/runs/{run_id}", response_model=RunOut)
async def get_run(
    run_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> RunOut:
    try:
        r = await uc.get_run(ctx, run_id)
        return RunOut.model_validate(r.model_dump())
    except (LCError, AppError) as exc:
        _raise(exc)
        raise


@router.get("/runs/{run_id}/trace", response_model=list[TraceOut])
async def get_trace(
    run_id: uuid.UUID,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> list[TraceOut]:
    try:
        items = await uc.get_run_trace(ctx, run_id)
        return [TraceOut.model_validate(t.model_dump()) for t in items]
    except (LCError, AppError) as exc:
        _raise(exc)
        raise


@router.post("/memory", response_model=MemoryOut)
async def update_memory(
    req: MemoryUpdateRequest,
    ctx: Annotated[Ctx, Depends(get_ctx)],
    uc: Annotated[LangChainUseCase, Depends(get_use_case)],
) -> MemoryOut:
    try:
        m = await uc.update_memory(
            ctx, conversation_id=req.conversation_id,
            memory_type=str(req.memory_type),
            messages=req.messages,
        )
        return MemoryOut.model_validate(m.model_dump())
    except (LCError, AppError) as exc:
        _raise(exc)
        raise
