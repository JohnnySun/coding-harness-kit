#!/usr/bin/env bash
# Wrapper for agent-kit install/validate/render.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
CMD="${1:-}"
shift || true
case "$CMD" in
  validate)
    exec uv run --project agent-kit/install python agent-kit/install/install.py validate "$@"
    ;;
  render)
    CLIENT="${CLIENT:-cursor}"
    exec env OUTPUT_ROOT="${OUTPUT_ROOT:-$ROOT}" \
      uv run --project agent-kit/install python agent-kit/install/install.py \
      install --client "$CLIENT" --dry-run "$@"
    ;;
  install)
    CLIENT="${CLIENT:?set CLIENT=cursor|cursor-cli|claude|codex|codex-native}"
    args=(install --client "$CLIENT")
    if [[ "${DRY_RUN:-}" == "1" ]]; then
      args+=(--dry-run)
    fi
    if [[ -n "${PLUGIN:-}" ]]; then
      # shellcheck disable=SC2206
      for p in $PLUGIN; do
        args+=(--with-optional-plugin="$p")
      done
    fi
    exec uv run --project agent-kit/install python agent-kit/install/install.py \
      "${args[@]}" "$@"
    ;;
  *)
    echo "usage: $0 {validate|render|install}" >&2
    echo "  CLIENT=cursor|cursor-cli|claude|codex|codex-native" >&2
    echo "  PLUGIN='name1 name2'  # optional plugins (install only)" >&2
    echo "  DRY_RUN=1             # install dry-run" >&2
    echo "  OUTPUT_ROOT=<dir>     # render/install output root" >&2
    exit 2
    ;;
esac
