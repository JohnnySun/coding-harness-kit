#!/usr/bin/env bash
# Install L1 git hooks (core.hooksPath → tools/harness/git-hooks).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
HOOK_DIR="$ROOT/tools/harness/git-hooks"
mkdir -p "$HOOK_DIR"
ln -sfn ../pre-commit.sh "$HOOK_DIR/pre-commit"
chmod +x "$ROOT/tools/harness/pre-commit.sh"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git config core.hooksPath tools/harness/git-hooks
  echo "core.hooksPath=tools/harness/git-hooks"
else
  echo "warning: not a git repo yet — run git init then re-run this script" >&2
fi
