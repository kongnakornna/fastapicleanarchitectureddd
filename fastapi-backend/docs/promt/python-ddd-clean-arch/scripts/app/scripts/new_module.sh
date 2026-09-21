#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# scripts/new_module.sh
# TH: Scaffold module DDD + Clean Arch (Linux / macOS)
# EN: DDD + Clean Arch module scaffolder
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GREEN='\033[0;92m'; YELLOW='\033[0;93m'; RED='\033[0;91m'
BLUE='\033[0;94m'; RESET='\033[0m'

banner() { echo -e "\n${BLUE}========================================${RESET}"; echo -e "${BLUE} $1${RESET}"; echo -e "${BLUE}========================================${RESET}"; }
kv() { echo -e "  ${YELLOW}$1${RESET} = $2"; }
ok() { echo -e "  ${GREEN}+${RESET} $1"; }

usage() {
  cat <<EOF

${BLUE}python-ddd-clean-arch — Scaffolder${RESET}

USAGE:
  new_module.sh <command> [args] [flags]

COMMANDS:
  new    <module> <layer> <prefix> [--sql --tests --docs --routes --force]
  all    <module> <layer> <prefix> [--force]
  sql    <module> <prefix>
  routes <module>
  test   <module>
  docs   <module> <layer> <prefix>
  help

EXAMPLES:
  ./scripts/new_module.sh new inventory 3 inv --sql --tests --docs --routes
  ./scripts/new_module.sh all sales 4 sal
EOF
}

derive_prefix() { echo "${1:0:3}"; }

ensure_dirs() {
  local m="$1"
  local base="$PROJECT_ROOT/app/modules/$m"
  for d in domain application infrastructure presentation; do
    mkdir -p "$base/$d"
    ok "$base/$d"
  done
  touch "$base/__init__.py"
  ok "$base/__init__.py"
}

write_module_files() {
  local m="$1"
  local base="$PROJECT_ROOT/app/modules/$m"
  local domain_files=(entities.py value_objects.py enums.py events.py exceptions.py __init__.py)
  local app_files=(interfaces.py use_cases.py mappers.py exceptions.py utils.py __init__.py)
  local infra_files=(models.py repositories.py caches.py services.py __init__.py)
  local pres_files=(routers.py schemas.py docs.py dependencies.py __init__.py)

  for f in "${domain_files[@]}"; do
    [ -f "$base/domain/$f" ] || { : > "$base/domain/$f"; ok "domain/$f"; }
  done
  for f in "${app_files[@]}"; do
    [ -f "$base/application/$f" ] || { : > "$base/application/$f"; ok "application/$f"; }
  done
  for f in "${infra_files[@]}"; do
    [ -f "$base/infrastructure/$f" ] || { : > "$base/infrastructure/$f"; ok "infrastructure/$f"; }
  done
  for f in "${pres_files[@]}"; do
    [ -f "$base/presentation/$f" ] || { : > "$base/presentation/$f"; ok "presentation/$f"; }
  done
}

write_sql_files() {
  local m="$1"
  local dir="$PROJECT_ROOT/db/migrations"
  mkdir -p "$dir"
  for v in "V001__create_${m}.sql" "V002__seed_${m}.sql" "V003__rollback_${m}.sql"; do
    [ -f "$dir/$v" ] || { echo "-- Module: $m" > "$dir/$v"; ok "db/migrations/$v"; }
  done
}

write_test_files() {
  local m="$1"
  local dir="$PROJECT_ROOT/tests"
  mkdir -p "$dir/unit" "$dir/integration" "$dir/property" "$dir/manual"
  for f in "unit/test_${m}.py" "unit/test_${m}_use_cases.py" \
           "integration/test_${m}_repository.py" "property/test_${m}_invariants.py" \
           "manual/manual_test_${m}.md"; do
    [ -f "$dir/$f" ] || { : > "$dir/$f"; ok "tests/$f"; }
  done
}

write_docs_files() {
  local m="$1" layer="$2" prefix="$3"
  local dir="$PROJECT_ROOT/docs"
  mkdir -p "$dir"
  for f in "README_${m}.md" "API_${m}.md"; do
    [ -f "$dir/$f" ] || { : > "$dir/$f"; ok "docs/$f"; }
  done
}

print_routes_hint() {
  local m="$1"
  echo
  echo -e "${YELLOW}[ROUTES]${RESET} เพิ่มที่ app/routes.py:"
  echo "  from app.modules.${m}.presentation.routers import router as ${m}_router"
  echo "  api_router.include_router(${m}_router)"
  echo
  echo -e "${YELLOW}[ROUTES]${RESET} เพิ่มที่ migrations/env.py:"
  echo "  from app.modules.${m}.infrastructure.models import ${m^}Model  # noqa: F401"
}

cmd="${1:-help}"; shift || true

case "$cmd" in
  new)
    module="${1:-}"; layer="${2:-0}"; prefix="${3:-}"; shift 3 || true
    [ -z "$module" ] && { echo -e "${RED}[ERROR]${RESET} missing module"; exit 1; }
    [ -z "$prefix" ] && prefix="$(derive_prefix "$module")"

    flag_sql=0 flag_tests=0 flag_docs=0 flag_routes=0
    for a in "$@"; do
      case "$a" in
        --sql) flag_sql=1 ;;
        --tests) flag_tests=1 ;;
        --docs) flag_docs=1 ;;
        --routes) flag_routes=1 ;;
        --force) ;;
      esac
    done

    banner "CREATE MODULE: $module"
    kv module "$module"; kv layer "$layer"; kv prefix "$prefix"
    echo
    ensure_dirs "$module"
    write_module_files "$module"
    [ "$flag_sql"    = 1 ] && write_sql_files "$module" "$prefix"
    [ "$flag_tests"  = 1 ] && write_test_files "$module"
    [ "$flag_docs"   = 1 ] && write_docs_files "$module" "$layer" "$prefix"
    [ "$flag_routes" = 1 ] && print_routes_hint "$module"
    echo -e "\n${GREEN}[OK]${RESET} module '$module' scaffolded"
    ;;

  all)
    module="${1:-}"; layer="${2:-0}"; prefix="${3:-}"
    [ -z "$module" ] && { echo -e "${RED}[ERROR]${RESET} missing module"; exit 1; }
    [ -z "$prefix" ] && prefix="$(derive_prefix "$module")"
    banner "CREATE ALL: $module"
    ensure_dirs "$module"
    write_module_files "$module"
    write_sql_files "$module" "$prefix"
    write_test_files "$module"
    write_docs_files "$module" "$layer" "$prefix"
    print_routes_hint "$module"
    echo -e "\n${GREEN}[OK]${RESET} all sections for '$module'"
    ;;

  sql)
    module="${1:-}"; prefix="${2:-}"; [ -z "$prefix" ] && prefix="$(derive_prefix "$module")"
    [ -z "$module" ] && { echo -e "${RED}[ERROR]${RESET} missing module"; exit 1; }
    banner "SQL: $module"
    write_sql_files "$module" "$prefix"
    ;;

  routes)
    module="${1:-}"; [ -z "$module" ] && { echo -e "${RED}[ERROR]${RESET} missing module"; exit 1; }
    banner "ROUTES: $module"
    print_routes_hint "$module"
    ;;

  test)
    module="${1:-}"; [ -z "$module" ] && { echo -e "${RED}[ERROR]${RESET} missing module"; exit 1; }
    banner "TESTS: $module"
    write_test_files "$module"
    ;;

  docs)
    module="${1:-}"; layer="${2:-0}"; prefix="${3:-}"
    [ -z "$module" ] && { echo -e "${RED}[ERROR]${RESET} missing module"; exit 1; }
    [ -z "$prefix" ] && prefix="$(derive_prefix "$module")"
    banner "DOCS: $module"
    write_docs_files "$module" "$layer" "$prefix"
    ;;

  help|--help|-h|"") usage ;;
  *) echo -e "${RED}[ERROR]${RESET} unknown command: $cmd"; usage; exit 1 ;;
esac