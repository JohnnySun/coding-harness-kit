#!/usr/bin/env bash
# Los Santos Customs (LSC) one-line installer (public GitHub / HTTPS).
# Public GitHub slug: los-santos-customs.
#
# Usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
#   curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
#
# Optional:
#   TARGET_DIR=my-kit CLIENT=cursor PLUGIN='superpowers mattpocock-skills' \
#     bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
#
# What it does:
#   1. Clone los-santos-customs with submodules
#   2. Install L1 git hooks
#   3. Install Agent-Kit for your editor/CLI (prompt or CLIENT=)
#   4. Run the public trusted suite
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/JohnnySun/los-santos-customs.git}"
REPO_REF="${REPO_REF:-main}"
DEFAULT_DIR="los-santos-customs"

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m ✓\033[0m  %s\n' "$*"; }
err()  { printf '\033[1;31m ✗\033[0m  %s\n' "$*" >&2; }
ask()  { printf '\033[1;33m ?\033[0m  %s ' "$*"; }

# Prefer /dev/tty so `curl | bash` can still prompt.
read_tty() {
  local __var="$1"
  local __prompt="${2:-}"
  if [[ -n "$__prompt" ]]; then
    ask "$__prompt"
  fi
  if [[ -r /dev/tty ]]; then
    # shellcheck disable=SC2162
    read -r "$__var" </dev/tty || true
  else
    # Non-interactive (CI / no tty): leave empty.
    printf -v "$__var" '%s' ""
    echo
  fi
}

for cmd in git curl bash; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    err "需要 $cmd，請先安裝。"
    exit 1
  fi
done

TARGET_DIR="${1:-${TARGET_DIR:-$DEFAULT_DIR}}"

if [[ -d "$TARGET_DIR/.git" ]]; then
  info "目錄 $TARGET_DIR 已存在，跳過 clone。"
else
  if [[ -e "$TARGET_DIR" ]]; then
    err "路徑 $TARGET_DIR 已存在但不是 git 倉庫，請換目錄或刪除後重試。"
    exit 1
  fi
  info "克隆 Los Santos Customs → $TARGET_DIR （含 submodule）…"
  git clone --recurse-submodules --branch "$REPO_REF" "$REPO_URL" "$TARGET_DIR"
  ok "克隆完成。"
fi

cd "$TARGET_DIR"

# Submodules may be missing if someone cloned without --recurse-submodules earlier.
info "確保 submodule 就緒…"
git submodule update --init --recursive
ok "submodule 就緒。"

info "安裝 git pre-commit hook…"
bash tools/harness/install-git-hooks.sh
ok "Git hooks 就緒。"

info "安裝 Agent-Kit（AI 工具 skills / hooks）"
echo "  可選 CLIENT: cursor | cursor-cli | claude | codex | codex-native"
echo "  可選 PLUGIN: superpowers mattpocock-skills"
echo

client="${CLIENT:-}"
if [[ -z "$client" ]]; then
  read_tty client "輸入 CLIENT（留空=安裝四個常用客戶端；輸入 skip=跳過）:"
fi

install_one() {
  local c="$1"
  info "Agent-Kit → $c"
  if [[ -n "${PLUGIN:-}" ]]; then
    CLIENT="$c" PLUGIN="$PLUGIN" bash tools/harness/agent-kit.sh install
  else
    CLIENT="$c" bash tools/harness/agent-kit.sh install
  fi
  ok "已安裝到 $c"
}

case "${client}" in
  skip|SKIP|none|NONE)
    echo "  跳過 Agent-Kit。之後可執行："
    echo "    CLIENT=cursor bash tools/harness/agent-kit.sh install"
    SKIP_SUITE=1
    ;;
  "")
    for c in cursor claude codex codex-native; do
      install_one "$c"
    done
    SKIP_SUITE=0
    ;;
  cursor|cursor-cli|claude|codex|codex-native)
    install_one "$client"
    SKIP_SUITE=0
    ;;
  *)
    err "未知 CLIENT: $client"
    echo "  請用: cursor | cursor-cli | claude | codex | codex-native | skip" >&2
    exit 2
    ;;
esac

if [[ "${SKIP_SUITE:-0}" == "1" ]]; then
  info "已跳過 Agent-Kit → 暫不跑公開可信集（symlink-health 需要本機 skills 樹）。"
  echo "  裝完 Agent-Kit 後請執行: bash tools/harness/test-harness.sh"
else
  info "跑公開可信集…"
  if bash tools/harness/test-harness.sh; then
    ok "公開可信集通過。"
  else
    err "公開可信集未通過——請檢查上方輸出（常見原因：submodule / uv / node 未就緒）。"
    exit 1
  fi
fi

echo
ok "全部完成！工作區: $(pwd)"
echo "  下一步:"
echo "    cd $TARGET_DIR"
echo "    # 可選：接入自己的 subject"
echo "    cp subjects/manifest.example.yaml subjects/manifest.yaml"
echo "    # 編輯 remotes 後："
echo "    bash tools/sync/sync-subjects.sh"
