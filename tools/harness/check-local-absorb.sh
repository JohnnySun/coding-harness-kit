#!/usr/bin/env bash
# Local absorb readiness — pin/checkout/harness-ready for private subjects.
# NOT the public trusted suite (that is test-harness.sh / L2 CI).
#
# Usage:
#   bash tools/harness/check-local-absorb.sh --all
#   bash tools/harness/check-local-absorb.sh <subject-id>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
exec python3 "$ROOT/tools/lib/subject_ready.py" "$@"
