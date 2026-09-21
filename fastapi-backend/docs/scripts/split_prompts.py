"""
split_prompts.py — แตก App_promt_AI_USE.md เป็น 65 ไฟล์
รองรับหลาย heading format:
  - ## 📄 Module 0.1: `money`
  - ### 🎯 ตัวอย่างเต็ม: Module `order`
  - ## 📄 Module 1.3–1.8: `user`, `employee`, ...
"""

import re
from pathlib import Path

SRC = Path(
    r"C:\github\fastapi-clean-architecture-ddd-erp-iot\docs\DOCS_APP\App_promt_AI_USE.md"
)
OUT = Path(
    r"C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend\docs\prompts"
)

LAYER_FOLDER = {
    0: "layer-0-core",
    1: "layer-1-foundation",
    2: "layer-2-money-path",
    3: "layer-3-goods-path",
    4: "layer-4-operations",
    5: "layer-5-intelligence",
    6: "layer-6-monitoring",
    7: "layer-7-templates",
}

# ─── Manual mapping: module → (layer, filename) ─────
# ใช้เป็น fallback ถ้า parse จาก heading ไม่ได้
MODULE_MAP: dict[str, int] = {
    # Layer 0
    "money": 0,
    "tenant_context": 0,
    "audit": 0,
    "idempotency": 0,
    "config": 0,
    "events": 0,
    # Layer 1
    "tenancy": 1,
    "authentication": 1,
    "user": 1,
    "employee": 1,
    "customer": 1,
    "supplier": 1,
    "product": 1,
    "pricing": 1,
    # Layer 2
    "order": 2,
    "invoice": 2,
    "ledger": 2,
    "payment": 2,
    "accounting_gateway": 2,
    "tax": 2,
    "reconciliation": 2,
    # Layer 3
    "inventory": 3,
    "warehouse": 3,
    "lot": 3,
    "production": 3,
    "recipe": 3,
    "quality": 3,
    "waste": 3,
    "procurement": 3,
    "traceability": 3,
    "agriculture": 3,
    "crop": 3,
    "soil": 3,
    "irrigation": 3,
    # Layer 4
    "transport": 4,
    "delivery": 4,
    "route": 4,
    "gps": 4,
    "retail": 4,
    "pos": 4,
    "shift": 4,
    "line_channel": 4,
    "promotion": 4,
    "loyalty": 4,
    "crm": 4,
    "campaign": 4,
    "support": 4,
    # Layer 5
    "reporting": 5,
    "analytics": 5,
    "forecast": 5,
    "kpi": 5,
    "satisfaction": 5,
    "recommendation": 5,
    "oee": 5,
    # Layer 6
    "iot": 6,
    "cctv": 6,
    "monitoring": 6,
    "backup": 6,
    "alerting": 6,
    "audit_viewer": 6,
    "maintenance": 6,
    "energy": 6,
    # Layer 7
    "health": 7,
    "example": 7,
    "blank": 7,
}


def extract_module_names(title: str) -> list[str]:
    """Extract module names from heading title."""
    names = re.findall(r"`([a-z_]+)`", title)
    return [n for n in names if n in MODULE_MAP]


def main() -> None:
    if not SRC.exists():
        print(f"❌ File not found: {SRC}")
        return

    text = SRC.read_text(encoding="utf-8")
    print(f"📖 Read: {SRC.name} ({len(text):,} chars)\n")

    # ─── หา Layer headings ───────────────────────────
    layer_re = re.compile(
        r"^#\s+📋\s+Layer\s+(\d+):\s+([A-Z\s&]+)—",
        re.MULTILINE,
    )
    layers = list(layer_re.finditer(text))
    print(f"🔍 Found {len(layers)} layer sections\n")

    # ─── หา Module headings ทุกแบบ ──────────────────
    module_re = re.compile(
        r"^#{2,3}\s+(?:"
        r"📄\s+Module\s+[\d.]+(?:–[\d.]+)?:\s*"  # ## 📄 Module X.Y:
        r"|🎯\s+ตัวอย่างเต็ม:\s+Module\s+"  # ### 🎯 ตัวอย่างเต็ม: Module
        r")(.+?)$",
        re.MULTILINE,
    )

    # รวมทุก heading (layer + module) แล้ว sort ตาม position
    all_headings = sorted(
        [(m.start(), "layer", i, m) for i, m in enumerate(layers)]
        + [(m.start(), "module", 0, m) for m in module_re.finditer(text)],
        key=lambda x: x[0],
    )

    # ─── Stats ───────────────────────────────────────
    total_created = 0
    total_skipped = 0
    layer_counts: dict[int, int] = {}

    # ─── วน loop ────────────────────────────────────
    for idx, (pos, kind, layer_idx, match) in enumerate(all_headings):
        if kind != "module":
            continue

        # หา layer ปัจจุบัน (layer heading ล่าสุดก่อน module นี้)
        current_layer = None
        for prev_pos, prev_kind, prev_idx, prev_match in reversed(all_headings[:idx]):
            if prev_kind == "layer":
                current_layer = int(prev_match.group(1))
                break

        if current_layer is None:
            continue

        # ─── ขอบเขตของ module ────────────────────────
        mod_start = match.start()
        mod_end = None
        for next_pos, next_kind, _, _ in all_headings[idx + 1 :]:
            # หยุดที่ module ถัดไป หรือ layer ถัดไป
            if next_kind in ("module", "layer"):
                mod_end = next_pos
                break
        if mod_end is None:
            mod_end = len(text)

        content = text[mod_start:mod_end].strip()
        title = match.group(1)

        # ─── Extract module names ────────────────────
        names = extract_module_names(title)

        # Fallback: ถ้าไม่มี backticks ให้ parse จาก title ตรงๆ
        if not names:
            m = re.match(r"`?([a-z_]+)`?", title.strip())
            if m and m.group(1) in MODULE_MAP:
                names = [m.group(1)]

        if not names:
            print(f"   ⚠️  No module name in: {title[:60]}")
            continue

        # ─── เขียนไฟล์ ──────────────────────────────
        folder = OUT / LAYER_FOLDER[current_layer]
        folder.mkdir(parents=True, exist_ok=True)
        layer_counts[current_layer] = layer_counts.get(current_layer, 0) + len(names)

        for name in names:
            # ถ้ามีหลาย name ให้เพิ่ม header "## Module `name`" แยก
            if len(names) > 1:
                module_content = f"## 📄 Module `{name}`\n\n{content}\n"
            else:
                module_content = content + "\n"

            file_path = folder / f"{name}.md"

            # Skip ถ้ามีไฟล์เดิม + มีเนื้อหา
            if file_path.exists() and file_path.stat().st_size > 100:
                print(f"   ⏭️  Layer {current_layer} | {name}.md (skip, exists)")
                total_skipped += 1
                continue

            file_path.write_text(module_content, encoding="utf-8")
            print(
                f"   ✅ Layer {current_layer} | {name}.md ({len(module_content):,} chars)"
            )
            total_created += 1

    # ─── สรุป ────────────────────────────────────────
    print()
    print("=" * 65)
    print("🎉 DONE!")
    print(f"   ✅ Created : {total_created}")
    print(f"   ⏭️  Skipped : {total_skipped}")
    print()
    print("📊 Files per layer:")
    for layer_num in sorted(layer_counts):
        expected = {0: 6, 1: 8, 2: 7, 3: 13, 4: 13, 5: 7, 6: 8, 7: 3}[layer_num]
        got = layer_counts[layer_num]
        status = "✅" if got == expected else f"⚠️  (expected {expected})"
        print(f"   Layer {layer_num} ({LAYER_FOLDER[layer_num]}): {got} {status}")
    print("=" * 65)


if __name__ == "__main__":
    main()
