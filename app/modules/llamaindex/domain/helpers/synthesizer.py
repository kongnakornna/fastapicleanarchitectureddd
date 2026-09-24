"""synthesizer — response synthesis strategies"""
from __future__ import annotations
from typing import Any


def build_context_block(nodes: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, n in enumerate(nodes, start=1):
        snippet = str(n.get("content", "")).strip().replace("\n", " ")
        lines.append(f"[{i}] {snippet}")
    return "\n\n".join(lines)


def build_synthesis_prompt(
    query: str, nodes: list[dict[str, Any]],
    *, mode: str = "compact",
) -> str:
    ctx = build_context_block(nodes)
    if mode == "refine":
        return (
            "Answer the question using the context. "
            "Refine iteratively if needed.\n\n"
            f"Question:\n{query}\n\nContext:\n{ctx}"
        )
    if mode == "tree_summarize":
        return (
            "Summarize each context chunk then combine to answer.\n\n"
            f"Question:\n{query}\n\nContext:\n{ctx}"
        )
    # compact / simple_summarize / default
    return (
        "Answer the question using ONLY the context. "
        "Cite sources as [1], [2], etc.\n\n"
        f"Question:\n{query}\n\nContext:\n{ctx}"
    )


async def synthesize_compact(
    llm: Any, *, tenant_id: Any, model: str, query: str,
    nodes: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = build_synthesis_prompt(query, nodes, mode="compact")
    result = await llm.chat(
        tenant_id=tenant_id, model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return _to_output(result)


async def synthesize_refine(
    llm: Any, *, tenant_id: Any, model: str, query: str,
    nodes: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = build_synthesis_prompt(query, nodes, mode="refine")
    result = await llm.chat(
        tenant_id=tenant_id, model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return _to_output(result)


async def synthesize_tree_summarize(
    llm: Any, *, tenant_id: Any, model: str, query: str,
    nodes: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = build_synthesis_prompt(query, nodes, mode="tree_summarize")
    result = await llm.chat(
        tenant_id=tenant_id, model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return _to_output(result)


def _to_output(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    content = getattr(result, "content", "") or ""
    usage = getattr(result, "usage", None)
    tokens = int(getattr(usage, "total_tokens", 0) or 0) \
        if usage is not None else 0
    return {"content": content, "tokens_used": tokens}
