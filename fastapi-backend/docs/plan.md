# CQRS Command Bus Rollout — Plan & Progress

## Objective
Finish the command-bus implementation across the FastAPI backend:
1. Shared bus lives in `app/core/commands.py` (verified present).
2. Add a per-module `commands.py` in each module's `application/` layer.
3. Ensure imports resolve (`uv run` verification).
4. Track progress in this file.

## Architecture Decision (user-confirmed)
- Build the command bus from scratch at `app/core/commands.py` — **no third-party library**.
- `app/core/commands.py` intentionally imports **no** `app.modules.*` (circular-import safety); modules import `app.core.commands`.

## Verified Facts
- `app/core/commands.py` exists (`Test-Path` → True).
- **No** `commands.py` exists anywhere under `app/modules` (recursive search empty).
- Authoritative module list (10): `audit`, `authentication`, `example`, `health`, `key`, `knowledge`, `notification`, `shared`, `user`, `websocket` (ignore `__pycache__`).
- All modules share a 4-layer structure; `application/` dirs contain `mappers.py`, `interfaces.py`, `utils.py`, `use_cases.py`, `exceptions.py`, `__init__.py`.
- All 10 target `application/` directories exist.

## Scope Decision (PENDING user answer)
Two options for per-module `commands.py` content:
- **A. Minimal placeholder/wiring files** — fastest; each file registers a single no-op/health command, later replaced.
- **B. Grounded domain-specific commands** — requires reading each module's domain first; higher value, slower.

## Tasks
- [ ] Write this `plan.md` (root) — *done now*
- [ ] Ask user scope clarification (A vs B)
- [ ] Create `app/modules/<module>/application/commands.py` × 10
- [ ] Verify imports: `uv run python -c "import app.modules.<module>.application.commands"` per module
- [ ] Update progress in this file

## Module Progress
| Module | commands.py | Imports verified |
|--------|-------------|------------------|
| audit | ⬜ | ⬜ |
| authentication | ⬜ | ⬜ |
| example | ⬜ | ⬜ |
| health | ⬜ | ⬜ |
| key | ⬜ | ⬜ |
| knowledge | ⬜ | ⬜ |
| notification | ⬜ | ⬜ |
| shared | ⬜ | ⬜ |
| user | ⬜ | ⬜ |
| websocket | ⬜ | ⬜ |
