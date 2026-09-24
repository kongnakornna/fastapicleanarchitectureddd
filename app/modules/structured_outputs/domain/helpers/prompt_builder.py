"""prompt_builder — inject schema into system prompt"""
from __future__ import annotations
import json
from typing import Optional


def build_system_prompt(
    schema: dict,
    *,
    strict: bool = False,
    description: str = "",
    base_prompt: Optional[str] = None,
) -> str:
    """TH: สร้าง system prompt พร้อม schema | EN: build system prompt"""
    parts: list[str] = []
    if base_prompt:
        parts.append(base_prompt.strip())

    parts.append(
        "You must respond with ONLY a valid JSON object that strictly "
        "conforms to the schema below. Do not wrap in markdown, do not "
        "add explanations."
    )
    if strict:
        parts.append(
            "Do NOT include any keys that are not declared in the schema."
        )
    if description:
        parts.append(f"Purpose: {description}")
    try:
        pretty = json.dumps(schema, indent=2, ensure_ascii=False)
    except Exception:
        pretty = str(schema)
    parts.append(f"JSON Schema:\n{pretty}")
    return "\n\n".join(parts)


def build_repair_prompt(errors: list[dict], previous: str) -> str:
    """TH: prompt สำหรับ repair | EN: repair prompt"""
    lines = [
        "Your previous output did not match the schema.",
        "Fix ONLY the following issues and return valid JSON only:",
    ]
    for e in errors[:10]:
        lines.append(f"- at {e.get('path', '$')}: {e.get('message', '')}")
    lines.append("")
    lines.append("Previous output:")
    lines.append(previous[:1500])
    return "\n".join(lines)
