#!/usr/bin/env bash
# L1: reject staging/committing private absorb trees (F5+, no escape).
# Doc placement: new docs/*.md must live under allowlisted subdirs.
# Also run trusted suite when harness surface is staged.
set -euo pipefail
# Prefer git toplevel — dirname("$0") breaks when this file is reached via
# tools/harness/git-hooks/pre-commit symlink (resolves to tools/harness/ → wrong ../..).
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT" ]]; then
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi
cd "$ROOT"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  staged="$(git diff --cached --name-only || true)"

  # snapshots/ + comparisons/ — never commit
  if printf '%s\n' "$staged" | grep -E '^(snapshots/|comparisons/)' >/dev/null; then
    echo "error: refusing to commit snapshots/** or comparisons/** (private absorb, no escape)" >&2
    exit 1
  fi

  # subjects/** except the public example manifest
  if printf '%s\n' "$staged" | grep -E '^subjects/' | grep -v -E '^subjects/manifest\.example\.yaml$' >/dev/null; then
    echo "error: refusing to commit subjects/** (private registry/checkout; only manifest.example.yaml is public)" >&2
    exit 1
  fi

  # Public-tree *content* desensitization (complements path deny above).
  # Catches home absolute paths / absolute checkout / private subject ids·remotes
  # embedded in otherwise-public staged files. Employer/org brand names are an
  # AI constraint (AGENTS.md), not a ban-list string match here.
  if [[ -n "$staged" ]]; then
    python3 tools/harness/public_tree_desensitize.py --staged
  fi

  DOCS_ALLOWED_SUBDIRS='specs|harness|onboarding|arch|rfcs'
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    if [[ "$path" == "docs/README.md" ]]; then
      continue
    fi
    if ! printf '%s\n' "$path" | grep -Eq "^docs/($DOCS_ALLOWED_SUBDIRS)/"; then
      echo "error: doc placement — refusing new $path" >&2
      echo "  Design docs → docs/specs/YYYYMMDD-slug/" >&2
      echo "  See docs/README.md" >&2
      exit 1
    fi
  done <<<"$(git diff --cached --name-only --diff-filter=A -- 'docs/*.md' 2>/dev/null || true)"

  if printf '%s\n' "$staged" | grep -E '^(specs/|docs/superpowers/|docs/technical-design/)' >/dev/null; then
    echo "error: refusing paths under sentinel zones (specs/, docs/superpowers/, docs/technical-design/)" >&2
    echo "  Design docs → docs/specs/YYYYMMDD-slug/" >&2
    exit 1
  fi

  if printf '%s\n' "$staged" | grep -E '^(tools/|subjects/manifest\.example\.yaml$|agent-kit/|docs/|testdata/|\.github/|\.cursor/skills/|\.agents/skills/|\.claude/skills/|\.codex/skills/)' >/dev/null; then
    bash tools/harness/test-harness.sh
  fi
fi
