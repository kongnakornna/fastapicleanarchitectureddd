#!/usr/bin/env python3
"""
run_all_modules.py — Run all AI module generators in dependency order.

Cross-platform (Windows/Linux/macOS). Handles:
  - Layer ordering (specific generators)
  - Optional generic AI modules (create_module_ai.py)
  - Conflict detection (generic vs specific)
  - --force flag with auto backup
  - Verify after each layer
  - Alembic migration

Usage:
    python run_all_modules.py                     # specific only (recommended)
    python run_all_modules.py --with-generic-ai   # + generic (⚠️ conflicts)
    python run_all_modules.py --only-layer "Layer 0 — Base"
    python run_all_modules.py --dry-run
    python run_all_modules.py --skip-migrate
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
#  UTF-8 FIX (Windows)
# ═══════════════════════════════════════════════════════════════
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════
VERSION = "2.0.0"


class C:
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; GRAY = "\033[90m"; BOLD = "\033[1m"; RESET = "\033[0m"


def info(msg: str) -> None: print(f"{C.CYAN}{msg}{C.RESET}", flush=True)
def ok(msg: str) -> None: print(f"  {C.GREEN}[OK]{C.RESET} {msg}", flush=True)
def warn(msg: str) -> None: print(f"  {C.YELLOW}[!!]{C.RESET} {msg}", flush=True)
def err(msg: str) -> None: print(f"  {C.RED}[XX]{C.RESET} {msg}", flush=True)
def skip(msg: str) -> None: print(f"  {C.GRAY}[--]{C.RESET} {msg}", flush=True)
def bold(msg: str) -> None: print(f"{C.BOLD}{msg}{C.RESET}", flush=True)


# ═══════════════════════════════════════════════════════════════
#  MODULE REGISTRY — Specific Generators (recommended)
# ═══════════════════════════════════════════════════════════════
SPECIFIC_MODULES: list[dict] = [
    # ─── Layer 0: Base ────────────────────────────────────────
    {
        "layer": "Layer 0 — Base",
        "script": "create_module_llm.py",
        "desc": "LLM (prefix=llm_)",
        "args": ["all", "llm", "5", "llm"],
    },
    {
        "layer": "Layer 0 — Base",
        "script": "create_module_embeddings.py",
        "desc": "Embeddings (prefix=emb_)",
        "args": ["all"],
    },
    # ─── Layer 1: Storage & Tools ─────────────────────────────
    {
        "layer": "Layer 1 — Storage & Tools",
        "script": "create_module_vector_db.py",
        "desc": "VectorDB (prefix=vdb_)",
        "args": ["all"],
    },
    {
        "layer": "Layer 1 — Storage & Tools",
        "script": "create_module_tool_calling.py",
        "desc": "Tool Calling (prefix=tool_)",
        "args": ["all", "tool_calling", "5", "tool"],
    },
    {
        "layer": "Layer 1 — Storage & Tools",
        "script": "create_module_structured_outputs.py",
        "desc": "Structured Outputs (prefix=so_)",
        "args": ["all"],
    },
    # ─── Layer 2: Retrieval & Frameworks ──────────────────────
    {
        "layer": "Layer 2 — Retrieval & Frameworks",
        "script": "create_module_hybrid_search.py",
        "desc": "Hybrid Search (prefix=hs_)",
        "args": ["all"],
    },
    {
        "layer": "Layer 2 — Retrieval & Frameworks",
        "script": "create_module_langchain.py",
        "desc": "LangChain (prefix=lc_)",
        "args": ["all"],
    },
    {
        "layer": "Layer 2 — Retrieval & Frameworks",
        "script": "create_module_llamaindex.py",
        "desc": "LlamaIndex (prefix=li_)",
        "args": ["all"],
    },
    # ─── Layer 3: Application ─────────────────────────────────
    {
        "layer": "Layer 3 — Application",
        "script": "create_module_rag.py",
        "desc": "RAG (prefix=rag_)",
        "args": ["all"],
    },
    {
        "layer": "Layer 3 — Application",
        "script": "create_module_ai_evaluation.py",
        "desc": "AI Evaluation (prefix=eval_)",
        "args": ["all"],
    },
]


# ═══════════════════════════════════════════════════════════════
#  OPTIONAL: Generic AI Modules (create_module_ai.py)
#  ⚠️ ใช้เมื่อต้องการโครงสร้างพื้นฐานเท่านั้น
#  ⚠️ ห้ามใช้ร่วมกับ specific generators ใน project เดียวกัน
# ═══════════════════════════════════════════════════════════════
GENERIC_AI_MODULES: list[dict] = [
    {
        "layer": "Generic AI (optional)",
        "script": "create_module_ai.py",
        "desc": "Generic RAG (⚠️ ชนกับ create_module_rag.py)",
        "args": ["all", "rag"],
        # conflict check: module dir + prefix
        "conflicts_with": {
            "module_dir": "app/modules/rag",
            "prefix": "rag",
            "specific_script": "create_module_rag.py",
        },
    },
    {
        "layer": "Generic AI (optional)",
        "script": "create_module_ai.py",
        "desc": "Generic Embeddings (⚠️ ชนกับ create_module_embeddings.py)",
        "args": ["all", "emb"],
        "conflicts_with": {
            "module_dir": "app/modules/emb",
            "prefix": "emb",
            "specific_script": "create_module_embeddings.py",
        },
    },
    {
        "layer": "Generic AI (optional)",
        "script": "create_module_ai.py",
        "desc": "Generic Tool (⚠️ ชนกับ create_module_tool_calling.py)",
        "args": ["all", "tool"],
        "conflicts_with": {
            "module_dir": "app/modules/tool",
            "prefix": "tool",
            "specific_script": "create_module_tool_calling.py",
        },
    },
    {
        "layer": "Generic AI (optional)",
        "script": "create_module_ai.py",
        "desc": "Generic Struct (⚠️ ชนกับ create_module_structured_outputs.py)",
        "args": ["all", "struct"],
        "conflicts_with": {
            "module_dir": "app/modules/struct",
            "prefix": "so",
            "specific_script": "create_module_structured_outputs.py",
        },
    },
    {
        "layer": "Generic AI (optional)",
        "script": "create_module_ai.py",
        "desc": "Generic Eval (⚠️ ชนกับ create_module_ai_evaluation.py)",
        "args": ["all", "eval"],
        "conflicts_with": {
            "module_dir": "app/modules/eval",
            "prefix": "eval",
            "specific_script": "create_module_ai_evaluation.py",
        },
    },
]


# ═══════════════════════════════════════════════════════════════
#  VERIFY TARGETS
# ═══════════════════════════════════════════════════════════════
VERIFY_TARGETS_SPECIFIC: list[dict] = [
    {"script": "create_module_llm.py", "args": ["verify", "llm", "5", "llm"]},
    {"script": "create_module_embeddings.py", "args": ["verify"]},
    {"script": "create_module_vector_db.py", "args": ["verify"]},
    {"script": "create_module_tool_calling.py", "args": ["verify", "tool_calling", "5", "tool"]},
    {"script": "create_module_structured_outputs.py", "args": ["verify"]},
    {"script": "create_module_hybrid_search.py", "args": ["verify"]},
    {"script": "create_module_langchain.py", "args": ["verify"]},
    {"script": "create_module_llamaindex.py", "args": ["verify"]},
    {"script": "create_module_rag.py", "args": ["verify"]},
    {"script": "create_module_ai_evaluation.py", "args": ["verify"]},
]

VERIFY_TARGETS_GENERIC: list[dict] = [
    {"script": "create_module_ai.py", "args": ["verify", "rag"]},
    {"script": "create_module_ai.py", "args": ["verify", "emb"]},
    {"script": "create_module_ai.py", "args": ["verify", "tool"]},
    {"script": "create_module_ai.py", "args": ["verify", "struct"]},
    {"script": "create_module_ai.py", "args": ["verify", "eval"]},
]


LAYERS_IN_ORDER: list[str] = [
    "Layer 0 — Base",
    "Layer 1 — Storage & Tools",
    "Layer 2 — Retrieval & Frameworks",
    "Layer 3 — Application",
    "Generic AI (optional)",
]


# ═══════════════════════════════════════════════════════════════
#  RUNNER
# ═══════════════════════════════════════════════════════════════
class Runner:
    def __init__(
        self,
        root: Path,
        force: bool = True,
        dry_run: bool = False,
        skip_migrate: bool = False,
        only_layer: str = "",
        with_generic_ai: bool = False,
        allow_conflicts: bool = False,
    ):
        self.root = root
        self.force = force
        self.dry_run = dry_run
        self.skip_migrate = skip_migrate
        self.only_layer = only_layer
        self.with_generic_ai = with_generic_ai
        self.allow_conflicts = allow_conflicts

        # log file
        self.log_dir = root / "logs"
        self.log_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"run_all_{ts}.log"
        self.log_handle = self.log_file.open("w", encoding="utf-8")

        # stats
        self.failed: list[str] = []
        self.succeeded: list[str] = []
        self.conflicts: list[dict] = []

    def close(self) -> None:
        try:
            self.log_handle.close()
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════
    #  Shell helpers
    # ═══════════════════════════════════════════════════════════
    def _run_cmd(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        capture: bool = True,
    ) -> tuple[int, str]:
        """Run command, tee output to log. Returns (returncode, output)."""
        self.log_handle.write(f"\n$ {' '.join(cmd)}\n")
        self.log_handle.flush()

        if self.dry_run:
            self.log_handle.write("[DRY-RUN] skipped\n")
            self.log_handle.flush()
            return 0, ""

        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd or self.root),
                capture_output=capture,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            out = (result.stdout or "") + (result.stderr or "")
            self.log_handle.write(out)
            self.log_handle.flush()
            return result.returncode, out
        except FileNotFoundError as exc:
            msg = f"command not found: {cmd[0]} ({exc})"
            self.log_handle.write(msg + "\n")
            self.log_handle.flush()
            return 127, msg
        except Exception as exc:
            msg = f"run failed: {exc}"
            self.log_handle.write(msg + "\n")
            self.log_handle.flush()
            return 1, msg

    # ═══════════════════════════════════════════════════════════
    #  Conflict detection
    # ═══════════════════════════════════════════════════════════
    def _detect_conflicts(self) -> list[dict]:
        """ตรวจ conflict ระหว่าง generic AI กับ specific generators"""
        conflicts: list[dict] = []

        if not self.with_generic_ai:
            return conflicts

        for g in GENERIC_AI_MODULES:
            c = g.get("conflicts_with")
            if not c:
                continue

            module_dir = self.root / c["module_dir"]
            specific_script = c["specific_script"]
            prefix = c["prefix"]

            # 1) module dir exists (specific generator สร้างไปแล้ว)
            if module_dir.exists():
                conflicts.append({
                    "generic": g["desc"],
                    "reason": f"module dir exists: {c['module_dir']}",
                    "resolved_by": specific_script,
                })
                continue

            # 2) prefix ชนกันใน migrations/versions
            versions_dir = self.root / "migrations" / "versions"
            if versions_dir.exists():
                matches = list(versions_dir.glob(f"{prefix}_001_*.py"))
                if matches:
                    conflicts.append({
                        "generic": g["desc"],
                        "reason": f"migration exists: {matches[0].name}",
                        "resolved_by": specific_script,
                    })

        return conflicts

    def _print_conflicts(self, conflicts: list[dict]) -> None:
        if not conflicts:
            return
        info("")
        warn("⚠  พบ conflict ระหว่าง generic AI กับ specific generators:")
        for i, c in enumerate(conflicts, 1):
            err(f"  {i}. {c['generic']}")
            err(f"     reason: {c['reason']}")
            err(f"     → ใช้ {c['resolved_by']} แทน")
        info("")
        warn("ถ้าต้องการใช้ generic AI จริง ๆ ให้:")
        print(f"     • ลบ module dir + migration ที่ชนกันก่อน")
        print(f"     • หรือใช้ --allow-conflicts (ไม่แนะนำ)")
        info("")

    # ═══════════════════════════════════════════════════════════
    #  Preflight checks
    # ═══════════════════════════════════════════════════════════
    def preflight(self) -> bool:
        info("─" * 60)
        info(f"[PREFLIGHT] checking environment (v{VERSION})")
        info("─" * 60)

        all_ok = True

        # 1) python
        ok(f"python: {sys.version.split()[0]}")

        # 2) project root
        if not self.root.exists():
            err(f"project root not found: {self.root}")
            return False
        ok(f"project root: {self.root}")

        # 3) app/app.py
        app_py = self.root / "app" / "app.py"
        if app_py.exists():
            ok("app.py: found")
        else:
            warn("app.py not found — update step may skip")

        # 4) migrations/env.py
        env_py = self.root / "migrations" / "env.py"
        if env_py.exists():
            ok("env.py: found")
        else:
            warn("env.py not found — update-env step may skip")

        # 5) migrations/versions
        versions = self.root / "migrations" / "versions"
        if versions.exists():
            n = len(list(versions.glob("*.py")))
            ok(f"migrations/versions: {n} files")
        else:
            warn("migrations/versions not found")

        # 6) specific generators
        info("")
        info("  Specific generators:")
        for m in SPECIFIC_MODULES:
            p = self.root / m["script"]
            if p.exists():
                ok(f"    {m['script']}")
            else:
                err(f"    NOT FOUND: {m['script']}")
                all_ok = False

        # 7) generic AI generator (optional)
        if self.with_generic_ai:
            info("")
            info("  Generic AI generator:")
            p = self.root / "create_module_ai.py"
            if p.exists():
                ok("    create_module_ai.py")
            else:
                err("    NOT FOUND: create_module_ai.py")
                all_ok = False

            # conflict detection
            self.conflicts = self._detect_conflicts()
            if self.conflicts:
                self._print_conflicts(self.conflicts)
                if not self.allow_conflicts:
                    err("  → abort (use --allow-conflicts to override)")
                    return False

        # 8) alembic
        info("")
        rc, out = self._run_cmd(["alembic", "--version"])
        if rc == 0:
            line = out.strip().splitlines()[0] if out else "ok"
            ok(f"alembic: {line}")
        else:
            warn("alembic not found — skip migrate")

        info("─" * 60)
        return all_ok

    # ═══════════════════════════════════════════════════════════
    #  Run one module
    # ═══════════════════════════════════════════════════════════
    def run_module(self, mod: dict) -> bool:
        script = mod["script"]
        desc = mod["desc"]
        args = list(mod["args"])

        # skip ถ้า conflict
        if self.conflicts and not self.allow_conflicts:
            for c in self.conflicts:
                if c["generic"] == desc:
                    skip(f"{desc} (conflict)")
                    return True

        if self.force and "--force" not in args:
            args.append("--force")

        info(f"▶ {desc}")
        info(f"  cmd: python {script} {' '.join(args)}")

        rc, out = self._run_cmd(["python", script, *args])
        if rc == 0:
            ok(f"  {desc} — DONE")
            self.succeeded.append(script)
            return True

        err(f"  {desc} — FAILED (rc={rc})")
        for line in (out or "").splitlines()[-8:]:
            err(f"    {line}")
        self.failed.append(script)
        return False

    # ═══════════════════════════════════════════════════════════
    #  Run by layer
    # ═══════════════════════════════════════════════════════════
    def run_layer(self, layer_name: str) -> bool:
        # รวม specific + generic
        mods = [m for m in SPECIFIC_MODULES if m["layer"] == layer_name]
        if self.with_generic_ai:
            mods += [m for m in GENERIC_AI_MODULES if m["layer"] == layer_name]

        if not mods:
            return True

        info("")
        info("┌" + "─" * 59 + "┐")
        info(f"│  {layer_name:<57}│")
        info("└" + "─" * 59 + "┘")

        all_ok = True
        for m in mods:
            if not self.run_module(m):
                all_ok = False
        return all_ok

    # ═══════════════════════════════════════════════════════════
    #  Verify
    # ═══════════════════════════════════════════════════════════
    def verify_all(self) -> bool:
        info("")
        info("┌" + "─" * 59 + "┐")
        info(f"│  {'VERIFY':<57}│")
        info("└" + "─" * 59 + "┘")

        all_ok = True

        # specific verify
        info("")
        info("  [Specific modules]")
        for v in VERIFY_TARGETS_SPECIFIC:
            script = v["script"]
            args = v["args"]
            info(f"▶ verify {script} {' '.join(args)}")
            rc, _ = self._run_cmd(["python", script, *args])
            if rc == 0:
                ok(f"  {script} — VERIFIED")
            else:
                warn(f"  {script} — VERIFY FAILED")
                all_ok = False

        # generic verify (optional)
        if self.with_generic_ai:
            info("")
            info("  [Generic AI modules]")
            for v in VERIFY_TARGETS_GENERIC:
                script = v["script"]
                args = v["args"]
                # skip ถ้า conflict
                if self.conflicts and not self.allow_conflicts:
                    mod_name = args[1] if len(args) > 1 else ""
                    if any(mod_name in c["generic"].lower() for c in self.conflicts):
                        skip(f"verify {script} {' '.join(args)} (conflict)")
                        continue
                info(f"▶ verify {script} {' '.join(args)}")
                rc, _ = self._run_cmd(["python", script, *args])
                if rc == 0:
                    ok(f"  {script} {' '.join(args)} — VERIFIED")
                else:
                    warn(f"  {script} {' '.join(args)} — VERIFY FAILED")
                    all_ok = False

        return all_ok

    # ═══════════════════════════════════════════════════════════
    #  Migrate
    # ═══════════════════════════════════════════════════════════
    def migrate(self) -> bool:
        if self.skip_migrate:
            warn("skip alembic (--skip-migrate)")
            return True

        info("")
        info("┌" + "─" * 59 + "┐")
        info(f"│  {'ALEMBIC MIGRATE':<57}│")
        info("└" + "─" * 59 + "┘")

        rc, _ = self._run_cmd(["alembic", "--version"])
        if rc != 0:
            warn("alembic not installed — skip migrate")
            return True

        info("▶ alembic heads")
        self._run_cmd(["alembic", "heads"])

        info("▶ alembic current")
        self._run_cmd(["alembic", "current"])

        info("▶ alembic upgrade head")
        rc, out = self._run_cmd(["alembic", "upgrade", "head"])
        if rc == 0:
            ok("alembic upgrade — DONE")
            return True

        err("alembic upgrade — FAILED")
        for line in (out or "").splitlines()[-10:]:
            err(f"  {line}")
        warn("Tip: ตรวจ down_revision ใน migrations/versions/*_add_*_tables.py")
        return False

    # ═══════════════════════════════════════════════════════════
    #  Main
    # ═══════════════════════════════════════════════════════════
    def run(self) -> int:
        t0 = time.monotonic()

        info("═" * 60)
        info("  RUN ALL AI MODULES")
        info(f"  VERSION         : {VERSION}")
        info(f"  PROJECT_ROOT    : {self.root}")
        info(f"  FORCE           : {self.force}")
        info(f"  DRY-RUN         : {self.dry_run}")
        info(f"  WITH GENERIC AI : {self.with_generic_ai}")
        info(f"  ALLOW CONFLICTS : {self.allow_conflicts}")
        info(f"  LOG             : {self.log_file}")
        info("═" * 60)

        # Preflight
        if not self.preflight():
            err("preflight failed — abort")
            return 1

        # Run layers
        for layer in LAYERS_IN_ORDER:
            # skip generic layer ถ้าไม่เปิด
            if layer == "Generic AI (optional)" and not self.with_generic_ai:
                skip(f"{layer} (--with-generic-ai not set)")
                continue

            # only-layer filter
            if self.only_layer and self.only_layer != layer:
                skip(f"{layer} (--only-layer={self.only_layer})")
                continue

            self.run_layer(layer)

        # Verify
        if not self.only_layer:
            self.verify_all()

        # Migrate
        if not self.only_layer:
            self.migrate()

        # Summary
        elapsed = time.monotonic() - t0
        info("")
        info("═" * 60)
        if self.failed:
            err(f"DONE with errors — {len(self.failed)} failed")
            for s in self.failed:
                err(f"  ✗ {s}")
        else:
            ok(f"ALL DONE — {len(self.succeeded)} modules")
        if self.conflicts:
            warn(f"  Conflicts skipped: {len(self.conflicts)}")
        info(f"  Elapsed : {elapsed:.1f}s")
        info(f"  Log     : {self.log_file}")
        info("═" * 60)
        print()

        info("Next steps:")
        print("  1. uvicorn app.app:app --reload")
        print("  2. open http://localhost:8000/docs")
        print("  3. import Postman: docs/postman/*.json")
        print()

        return 0 if not self.failed else 1


# ═══════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════
HELP = f"""
═══════════════════════════════════════════════════════════════
  run_all_modules.py — All AI Module Generators v{VERSION}
═══════════════════════════════════════════════════════════════

  USAGE
    python run_all_modules.py [options]

  OPTIONS
    --project-root PATH   project root (default: .)
    --no-force            do NOT overwrite existing files
    --dry-run             print commands, don't execute
    --skip-migrate        skip alembic upgrade head
    --only-layer NAME     run only one layer
    --with-generic-ai     also run create_module_ai.py
                          ⚠️ may conflict with specific generators
    --allow-conflicts     override conflict check (dangerous)
    -h, --help            show this help

  LAYERS (in order)
    Layer 0 — Base               : LLM, Embeddings
    Layer 1 — Storage & Tools    : VectorDB, ToolCalling, StructuredOutputs
    Layer 2 — Retrieval & Frameworks : HybridSearch, LangChain, LlamaIndex
    Layer 3 — Application        : RAG, AI Evaluation
    Generic AI (optional)        : rag, emb, tool, struct, eval (generic)

  EXAMPLES
    # Standard run (recommended)
    python run_all_modules.py

    # Run only Layer 0
    python run_all_modules.py --only-layer "Layer 0 — Base"

    # Dry-run to preview
    python run_all_modules.py --dry-run

    # Include generic AI (⚠️ conflict check runs first)
    python run_all_modules.py --with-generic-ai

    # Skip migrate (if already migrated)
    python run_all_modules.py --skip-migrate

  RESULTS
    Swagger  : http://localhost:8000/docs
    Postman  : docs/postman/*.json
    Log      : logs/run_all_<timestamp>.log
═══════════════════════════════════════════════════════════════
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(
        add_help=False,
        description="Run all AI module generators in dependency order",
    )
    parser.add_argument(
        "--project-root", default=".",
        help="project root (default: current dir)",
    )
    parser.add_argument(
        "--no-force", action="store_true",
        help="do NOT overwrite existing files (skip if exists)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print commands but don't run",
    )
    parser.add_argument(
        "--skip-migrate", action="store_true",
        help="skip alembic upgrade head",
    )
    parser.add_argument(
        "--only-layer", default="",
        help="run only one layer (e.g. 'Layer 0 — Base')",
    )
    parser.add_argument(
        "--with-generic-ai", action="store_true",
        help="also run create_module_ai.py (⚠️ may conflict)",
    )
    parser.add_argument(
        "--allow-conflicts", action="store_true",
        help="override conflict check (dangerous)",
    )
    parser.add_argument(
        "-h", "--help", action="store_true",
        help="show help",
    )
    args, _ = parser.parse_known_args()

    if args.help:
        print(HELP)
        return 0

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"project root not found: {root}")
        return 1

    runner = Runner(
        root=root,
        force=not args.no_force,
        dry_run=args.dry_run,
        skip_migrate=args.skip_migrate,
        only_layer=args.only_layer,
        with_generic_ai=args.with_generic_ai,
        allow_conflicts=args.allow_conflicts,
    )

    try:
        rc = runner.run()
    except KeyboardInterrupt:
        err("\nAborted by user")
        rc = 130
    finally:
        runner.close()

    return rc


if __name__ == "__main__":
    sys.exit(main())