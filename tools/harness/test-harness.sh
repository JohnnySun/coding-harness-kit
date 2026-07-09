#!/usr/bin/env bash
# Harness-dev 一鍵公開可信集（L2 同構）。窄跑不算收環。
# 不含私有 subjects/** pin/checkout/snapshot 狀態檢查。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
node --test tools/harness/hook-router.test.mjs tools/harness/prompt-skill-router.test.mjs tools/harness/advisor-card.test.mjs
python3 -m unittest discover -s tools/harness -p 'test_agent_kit_install.py' -v
python3 -m unittest discover -s tools/harness -p 'test_subject_gates.py' -v
python3 -m unittest discover -s tools/harness -p 'test_public_tree_desensitize.py' -v
# install.py unit tests (plugin collision / resolve)
(cd agent-kit/install && uv run python -m unittest discover -s tests -v)
python3 tools/harness/checks.py "$@"
