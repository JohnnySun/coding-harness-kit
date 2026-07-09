#!/usr/bin/env bash
# Minimal coding-harness trusted suite (fixture).
# Exit 0 = green. Used by tools/harness/check_subject_gates.py in CI.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Gate shape: require AGENTS.md (constraint layer present)
test -f AGENTS.md

# Gate shape: refuse "claimed done" without this script existing (tautology for demo)
test -x scripts/harness/test-harness.sh || test -f scripts/harness/test-harness.sh

echo "✔ demo-coding-harness-min trusted suite OK"
