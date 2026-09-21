"""
split_prompts.py — แตก App_promt_AI_USE.md เป็น 65 ไฟล์
รองรับ heading หลาย format:
  - ## 📄 Module 0.1: `money`
  - ### 🎯 ตัวอย่างเต็ม: Module `order`
  - ## 📄 Module 1.3–1.8: `user`, `employee`, ...
  - ### 📄 Module 7.2: `example` (Reference Implementation)
  - ## 📄 Module `user`                       ← NEW: no version number
  - ## 📄 Module 6.11: `audit_trail`          ← NEW: module number >= 10

Usage:
    python scripts/split_prompts.py
    python scripts/split_prompts.py --dry-run     # preview
    python scripts/split_prompts.py --clean       # ลบเก่าก่อน
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════

SRC = Path(r"C:\github\fastapi-clean-architecture-ddd-erp-iot\docs\DOCS_APP\App_promt_AI_USE.md")
OUT = Path(r"C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend\docs\prompts")

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

EXPECTED_COUNT = {0: 6, 1: 8, 2: 7, 3: 13, 4: 13, 5: 7, 6: 11, 7: 3}

# Module → layer mapping (fallback ถ้า parse จาก heading ไม่ได้)
MODULE_MAP: dict[str, int] = {
    # Layer 0: Core
    "money": 0, "tenant_context": 0, "audit": 0,
    "idempotency": 0, "config": 0, "events": 0,
    # Layer 1: Foundation
    "tenancy": 1, "authentication": 1, "user": 1, "employee": 1,
    "customer": 1, "supplier": 1, "product": 1, "pricing": 1,
    # Layer 2: Money Path
    "order": 2, "invoice": 2, "ledger": 2, "payment": 2,
    "accounting_gateway": 2, "tax": 2, "reconciliation": 2,
    # Layer 3: Goods Path
    "inventory": 3, "warehouse": 3, "lot": 3, "production": 3,
    "recipe": 3, "quality": 3, "waste": 3, "procurement": 3,
    "traceability": 3, "agriculture": 3, "crop": 3, "soil": 3, "irrigation": 3,
    # Layer 4: Operations
    "transport": 4, "delivery": 4, "route": 4, "gps": 4, "retail": 4,
    "pos": 4, "shift": 4, "line_channel": 4, "promotion": 4, "loyalty": 4,
    "crm": 4, "campaign": 4, "support": 4,
    # Layer 5: Intelligence
    "reporting": 5, "analytics": 5, "forecast": 5, "kpi": 5,
    "satisfaction": 5, "recommendation": 5, "oee": 5,
    # Layer 6: Monitoring
    "iot": 6, "alert": 6, "notification": 6, "health": 6,
    "log": 6, "trace": 6, "metrics": 6, "incident": 6,
    "sla": 6, "dashboard": 6, "anomaly": 6, "audit_trail": 6,
    # Layer 7: Templates
    "health_check": 7, "example": 7, "blank": 7,
}

# Alias: บางไฟล์ต้นทางอาจใช้ชื่อต่างจากที่คาด
MODULE_ALIAS = {
    "health_monitor": 6,     # บางเอกสารใช้ชื่อนี้
    "health_check": 7,
    "example_impl": 7,
    "empty": 7,
}


# ═══════════════════════════════════════════════════════════════════
# PATTERNS
# ═══════════════════════════════════════════════════════════════════

# Layer heading:
#   # 📋 Layer 0 (Core) — ...
#   # 📋 Layer 5 (Intelligence) — ...
LAYER_RE = re.compile(
    r"^#\s+(?:📋\s+)?Layer\s+(\d+)(?:\s*\(([^)]+)\))?",
    re.MULTILINE,
)

# Module heading รองรับทุก format:
#   ## 📄 Module 0.1: `money`
#   ### 🎯 ตัวอย่างเต็ม: Module `order`
#   ## 📄 Module 1.3–1.8: `user`, `employee`, `customer`, ...
#   ### 📄 Module 7.2: `example` (Reference Implementation)
#   ## 📄 Module `user`                        ← NEW: bare backtick name
#   ## 📄 Module 6.11: `audit_trail`           ← NEW: 2-digit module number
MODULE_RE = re.compile(
    r"^(#{2,3})\s+"
    r"(?:"
    # 1) "## 📄 Module X.Y: `name`" (versioned, colon required)
    r"📄\s+Module\s+[\d]+(?:\.[\d]+)?(?:\s*[–\-]\s*[\d.]+)?\s*:\s*"
    # 2) "### 🎯 ตัวอย่างเต็ม: Module `name`"
    r"|🎯\s+ตัวอย่างเต็ม\s*:\s*Module\s+"
    # 3) "### 📄 Module `name` (Reference Implementation)"
    r"|📄\s+Module\s+`([a-z_]+)`\s*(?:\([^)]*\))?\s*:?\s*"
    # 4) "## 📄 Module `name`"  — bare backtick, no colon, no parens
    r"|📄\s+Module\s+`([a-z_]+)`\s*$"
    r")"
    r"(.+?)$",
    re.MULTILINE,
)

# backtick-name: `money`, `tenant_context`
BACKTICK_RE = re.compile(r"`([a-z_]+)`")


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def extract_module_names(title: str) -> list[str]:
    """
    Extract module names จาก heading title
    รองรับ:
      "`money`"                           → ["money"]
      "`user`, `employee`, `customer`"    → ["user", "employee", "customer"]
      "`example` (Reference Implementation)" → ["example"]
      "`user`"                            → ["user"]
    """
    names = BACKTICK_RE.findall(title)
    # filter เฉพาะชื่อที่อยู่ใน MODULE_MAP หรือ ALIAS
    valid = [n for n in names if n in MODULE_MAP or n in MODULE_ALIAS]
    return valid


def detect_layer_for_name(name: str, fallback: int | None = None) -> int:
    """หา layer ของ module"""
    if name in MODULE_MAP:
        return MODULE_MAP[name]
    if name in MODULE_ALIAS:
        return MODULE_ALIAS[name]
    if fallback is not None:
        return fallback
    return -1


def clean_output() -> None:
    """ลบ output directory เก่า"""
    if OUT.exists():
        print(f"🗑️  Removing old: {OUT}")
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(description="Split prompts MD → files")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--clean", action="store_true", help="Remove old output first")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    if not SRC.exists():
        print(f"❌ File not found: {SRC}")
        print(f"   Please check the path in SRC variable.")
        return 1

    text = SRC.read_text(encoding="utf-8")
    print(f"📖 Read: {SRC.name}")
    print(f"   Size: {len(text):,} chars, {len(text.splitlines()):,} lines\n")

    if args.clean and args.dry_run:
        print("⚠️  --clean ignored in --dry-run mode")
    elif args.clean:
        clean_output()

    # ─── หา layer headings ────────────────────────────
    layers = list(LAYER_RE.finditer(text))
    print(f"🔍 Found {len(layers)} layer headings")

    if not layers:
        print("⚠️  No layer headings found. Please check format.")
        print("   Expected: '# 📋 Layer 0 (Core) — ...'")
        return 1

    for m in layers:
        print(f"   - Layer {m.group(1)}: {m.group(2) or '?'}")

    # ─── หา module headings ───────────────────────────
    modules = list(MODULE_RE.finditer(text))
    print(f"\n🔍 Found {len(modules)} module headings")

    if not modules:
        print("\n⚠️  No module headings found. Showing sample headings:")
        for line in text.splitlines()[:30]:
            if line.startswith("#"):
                print(f"   > {line[:80]}")
        return 1

    # ─── รวม headings ทั้งหมด sort ตาม position ──────
    all_headings = sorted(
        [(m.start(), "layer", m) for m in layers] +
        [(m.start(), "module", m) for m in modules],
        key=lambda x: x[0],
    )

    # ─── วน loop ─────────────────────────────────────
    total_created = 0
    total_skipped = 0
    total_empty = 0
    layer_counts: dict[int, int] = {}
    warnings: list[str] = []

    for idx, (pos, kind, match) in enumerate(all_headings):
        if kind != "module":
            continue

        # หา layer ปัจจุบัน (heading layer ล่าสุดก่อน module นี้)
        current_layer = None
        for prev_pos, prev_kind, prev_match in reversed(all_headings[:idx]):
            if prev_kind == "layer":
                current_layer = int(prev_match.group(1))
                break

        if current_layer is None:
            warnings.append(f"⚠️  No layer for module at pos {pos}")
            continue

        # ─── ขอบเขตของ module ────────────────────────
        mod_start = match.start()
        mod_end = len(text)
        for next_pos, next_kind, _ in all_headings[idx + 1:]:
            if next_kind in ("module", "layer"):
                mod_end = next_pos
                break

        content = text[mod_start:mod_end].strip()
        # title = last group ของ MODULE_RE (group ที่ไม่ใช่ None)
        title = match.group(match.lastindex).strip() if match.lastindex else ""
        # เผื่อกรณี heading เป็น "## 📄 Module `user`" ที่ group จับได้ที่ 3
        # (backtick name) — ใช้ full match text ประกอบ
        full_line = match.group(0)

        # ─── Extract module names ────────────────────
        # ลองดึงจาก title ก่อน
        names = extract_module_names(title)

        # Fallback: ดึงจาก full match line (มี backtick name ใน group 3/4)
        if not names:
            names = extract_module_names(full_line)

        # Fallback 2: parse title ตรงๆ
        if not names:
            m2 = re.match(r"`?([a-z_]+)`?", title)
            if m2 and (m2.group(1) in MODULE_MAP or m2.group(1) in MODULE_ALIAS):
                names = [m2.group(1)]

        if not names:
            warnings.append(f"⚠️  No module in heading: {full_line[:60]}")
            continue

        # ─── เขียนไฟล์ ───────────────────────────────
        folder = OUT / LAYER_FOLDER[current_layer]
        if not args.dry_run:
            folder.mkdir(parents=True, exist_ok=True)

        for name in names:
            # ใช้ layer จาก mapping เป็นหลัก (แก้ปัญหาชื่อซ้ำ)
            actual_layer = detect_layer_for_name(name, fallback=current_layer)
            actual_folder = OUT / LAYER_FOLDER[actual_layer]

            if not args.dry_run:
                actual_folder.mkdir(parents=True, exist_ok=True)

            # ถ้าหลาย name ใน heading เดียว → แยก header ให้
            if len(names) > 1:
                module_content = f"## 📄 Module `{name}`\n\n{content}\n"
            else:
                module_content = content + "\n"

            file_path = actual_folder / f"{name}.md"

            # Skip ถ้ามีไฟล์เดิม + มีเนื้อหา + ไม่ force
            if file_path.exists() and file_path.stat().st_size > 100 and not args.force:
                print(f"   ⏭️  Layer {actual_layer} | {name}.md (skip)")
                total_skipped += 1
                layer_counts[actual_layer] = layer_counts.get(actual_layer, 0) + 1
                continue

            if args.dry_run:
                print(f"   [DRY] Layer {actual_layer} | {name}.md ({len(module_content):,} chars)")
            else:
                if len(module_content) < 100:
                    warnings.append(f"⚠️  Empty content: {name}.md ({len(module_content)} chars)")
                    total_empty += 1
                    continue

                file_path.write_text(module_content, encoding="utf-8")
                print(f"   ✅ Layer {actual_layer} | {name}.md ({len(module_content):,} chars)")

            total_created += 1
            layer_counts[actual_layer] = layer_counts.get(actual_layer, 0) + 1

    # ─── สรุป ────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"🎉 DONE!  Mode: {'DRY-RUN' if args.dry_run else 'WRITE'}")
    print(f"   ✅ Created : {total_created}")
    print(f"   ⏭️  Skipped : {total_skipped}")
    if total_empty:
        print(f"   ⚠️  Empty   : {total_empty}")

    print()
    print("📊 Files per layer:")
    total_expected = 0
    total_actual = 0
    for layer_num in sorted(EXPECTED_COUNT):
        expected = EXPECTED_COUNT[layer_num]
        got = layer_counts.get(layer_num, 0)
        total_expected += expected
        total_actual += got
        status = "✅" if got == expected else f"⚠️  (expected {expected})"
        print(f"   Layer {layer_num} ({LAYER_FOLDER[layer_num]:<22}): {got:>2} {status}")

    print(f"\n   TOTAL: {total_actual}/{total_expected} "
          f"{'✅' if total_actual == total_expected else '⚠️'}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings:")
        for w in warnings[:10]:
            print(f"   {w}")
        if len(warnings) > 10:
            print(f"   ... and {len(warnings) - 10} more")

    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())