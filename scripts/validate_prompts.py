"""
validate_prompts.py — ตรวจสอบไฟล์ prompts ครบ 65 + มีเนื้อหาจริง

Usage:
    python scripts/validate_prompts.py
    python scripts/validate_prompts.py --verbose
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

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

# NOTE: ตั้งชื่อไฟล์ให้ตรงกับที่ split_prompts.py สร้าง
#   - Layer 6 ใช้ "health"     (จาก Module 6.3: `health`)
#   - Layer 7 ใช้ "health_check" (จาก Module 7.1)
EXPECTED: dict[int, list[str]] = {
    0: ["money", "tenant_context", "audit", "idempotency", "config", "events"],
    1: ["tenancy", "authentication", "user", "employee",
        "customer", "supplier", "product", "pricing"],
    2: ["order", "invoice", "ledger", "payment",
        "accounting_gateway", "tax", "reconciliation"],
    3: ["inventory", "warehouse", "lot", "production", "recipe",
        "quality", "waste", "procurement", "traceability",
        "agriculture", "crop", "soil", "irrigation"],
    4: ["transport", "delivery", "route", "gps", "retail",
        "pos", "shift", "line_channel", "promotion", "loyalty",
        "crm", "campaign", "support"],
    5: ["reporting", "analytics", "forecast", "kpi",
        "satisfaction", "recommendation", "oee"],
    6: ["iot", "alert", "notification", "health", "log",
        "trace", "metrics", "incident", "sla", "dashboard",
        "anomaly", "audit_trail"],
    7: ["health_check", "example", "blank"],
}

MIN_SIZE = 200  # bytes


def validate_file(path: Path) -> tuple[bool, str]:
    """ตรวจไฟล์ 1 ไฟล์"""
    if not path.exists():
        return False, "missing"
    size = path.stat().st_size
    if size < MIN_SIZE:
        return False, f"too small ({size} bytes)"
    content = path.read_text(encoding="utf-8", errors="replace")
    # ต้องมี heading "Module"
    if not re.search(r"#+\s+.*Module", content):
        return False, "no Module heading"
    return True, f"OK ({size:,} bytes)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    print("=" * 70)
    print("  VALIDATOR — docs/prompts/")
    print("=" * 70)
    print(f"  Root: {OUT}")
    print(f"  Min size: {MIN_SIZE} bytes")
    print()

    if not OUT.exists():
        print(f"❌ Directory not found: {OUT}")
        return 1

    total_ok = 0
    total_missing = 0
    total_problems: list[tuple[str, str]] = []

    for layer_num in sorted(EXPECTED):
        names = EXPECTED[layer_num]
        folder = OUT / LAYER_FOLDER[layer_num]

        print(f"\n📁 Layer {layer_num} ({LAYER_FOLDER[layer_num]})")
        print(f"   Expected: {len(names)} files")

        if not folder.exists():
            print(f"   ❌ Folder missing!")
            for name in names:
                total_missing += 1
                total_problems.append((f"L{layer_num}/{name}", "folder missing"))
            continue

        ok_in_layer = 0
        for name in names:
            path = folder / f"{name}.md"
            ok, msg = validate_file(path)
            if ok:
                ok_in_layer += 1
                total_ok += 1
                if args.verbose:
                    print(f"   ✅ {name}.md — {msg}")
            else:
                total_missing += 1
                total_problems.append((f"L{layer_num}/{name}.md", msg))
                print(f"   ❌ {name}.md — {msg}")

        status = "✅" if ok_in_layer == len(names) else f"⚠️  {ok_in_layer}/{len(names)}"
        print(f"   → {status}")

    # ─── สรุป ────────────────────────────────────────
    total_expected = sum(len(v) for v in EXPECTED.values())
    print()
    print("=" * 70)
    print(f"  ✅ PASS : {total_ok}/{total_expected}")
    print(f"  ❌ FAIL : {total_missing}/{total_expected}")

    if total_problems:
        print(f"\n  Problems ({len(total_problems)}):")
        for name, reason in total_problems[:20]:
            print(f"    - {name}: {reason}")
        if len(total_problems) > 20:
            print(f"    ... and {len(total_problems) - 20} more")

    print("=" * 70)
    return 0 if total_missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())