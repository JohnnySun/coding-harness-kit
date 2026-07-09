#!/usr/bin/env bash
# Sync harness subjects from subjects/manifest.yaml into subjects/<id>/checkout/.
# Default: shell clone + default_submodules only (no business trees).
#
# Planned submodule set comes ONLY from tools/sync/lib/planned_submodules.py
# (trusted-suite binding — do not inline a second parser here).
#
# Usage:
#   tools/sync/sync-subjects.sh                 # all subjects
#   tools/sync/sync-subjects.sh <id>            # one subject
#   tools/sync/sync-subjects.sh <id> --with server,docs
#   tools/sync/sync-subjects.sh --latest        # reset shell to origin/<branch> tip
#   tools/sync/sync-subjects.sh <id> --pin      # rewrite pin.json after sync
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST="$ROOT/subjects/manifest.yaml"
SUBJECTS_DIR="$ROOT/subjects"
PLANNED_PY="$ROOT/tools/sync/lib/planned_submodules.py"

die() { echo "error: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"; }

need git
need python3
[[ -f "$MANIFEST" ]] || die "manifest not found: $MANIFEST"
[[ -f "$PLANNED_PY" ]] || die "planned_submodules lib missing: $PLANNED_PY"

LATEST=0
WRITE_PIN=0
WITH_EXTRA=""
TARGETS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) shift ;;
    --latest) LATEST=1; shift ;;
    --pin) WRITE_PIN=1; shift ;;
    --with)
      [[ $# -ge 2 ]] || die "--with needs a comma-separated submodule list"
      WITH_EXTRA="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '2,14p' "$0"
      exit 0
      ;;
    -*)
      die "unknown flag: $1"
      ;;
    *)
      if [[ -z "$TARGETS" ]]; then
        TARGETS="$1"
      else
        TARGETS="$TARGETS $1"
      fi
      shift
      ;;
  esac
done

list_subjects() {
  python3 - "$MANIFEST" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).resolve().parents[1] / "tools" / "sync" / "lib"))
# argv[1] is manifest path — parents: subjects -> ROOT
root = Path(sys.argv[1]).resolve().parents[1]
sys.path.insert(0, str(root / "tools" / "sync" / "lib"))
from planned_submodules import list_subjects
print("\n".join(list_subjects(Path(sys.argv[1]).read_text(encoding="utf-8"))))
PY
}

subject_field() {
  local id="$1" field="$2"
  python3 - "$MANIFEST" "$id" "$field" <<'PY'
import sys
from pathlib import Path
manifest, sid, field = sys.argv[1], sys.argv[2], sys.argv[3]
root = Path(manifest).resolve().parents[1]
sys.path.insert(0, str(root / "tools" / "sync" / "lib"))
from planned_submodules import subject_scalar, default_submodules, harness_paths
text = Path(manifest).read_text(encoding="utf-8")
if field == "default_submodules":
    print("\n".join(default_submodules(text, sid)))
elif field == "harness_paths":
    print("\n".join(harness_paths(text, sid)))
else:
    print(subject_scalar(text, sid, field))
PY
}

planned_for() {
  local id="$1"
  if [[ -n "$WITH_EXTRA" ]]; then
    python3 "$PLANNED_PY" "$MANIFEST" "$id" --with "$WITH_EXTRA"
  else
    python3 "$PLANNED_PY" "$MANIFEST" "$id"
  fi
}

if [[ -z "$TARGETS" ]]; then
  TARGETS="$(list_subjects | tr '\n' ' ')"
fi
[[ -n "$(echo "$TARGETS" | tr -d '[:space:]')" ]] || die "no subjects in manifest"

resolve_submodule_name() {
  local checkout="$1" path_or_name="$2"
  local name
  name="$(
    git -C "$checkout" config -f .gitmodules --get-regexp '^submodule\..*\.path$' \
      | awk -v p="$path_or_name" '$2 == p {
          n = $1
          sub(/^submodule\./, "", n)
          sub(/\.path$/, "", n)
          print n
          exit
        }'
  )"
  if [[ -n "$name" ]]; then
    echo "$name"
    return 0
  fi
  if git -C "$checkout" config -f .gitmodules --get "submodule.$path_or_name.path" >/dev/null 2>&1; then
    echo "$path_or_name"
    return 0
  fi
  return 1
}

sync_one() {
  local id="$1"
  local remote branch checkout
  remote="$(subject_field "$id" remote)"
  branch="$(subject_field "$id" default_branch)"
  checkout="$SUBJECTS_DIR/$id/checkout"

  mkdir -p "$SUBJECTS_DIR/$id"

  if [[ ! -d "$checkout/.git" ]]; then
    echo "==> clone $id ($remote @ $branch)"
    git clone --depth 1 --branch "$branch" "$remote" "$checkout"
  else
    echo "==> update $id"
    git -C "$checkout" remote set-url origin "$remote"
    git -C "$checkout" fetch --depth 1 origin "$branch"
    if [[ "$LATEST" -eq 1 ]]; then
      git -C "$checkout" checkout -B "$branch" "origin/$branch"
    else
      git -C "$checkout" checkout "$branch" 2>/dev/null \
        || git -C "$checkout" checkout -B "$branch" "origin/$branch"
    fi
  fi

  local subs=""
  local line
  while IFS= read -r line; do
    [[ -n "$line" ]] && subs="$subs $line"
  done < <(planned_for "$id")
  subs="$(echo "$subs" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

  if [[ -n "$subs" ]]; then
    echo "==> init submodules for $id: $subs"
    local s name path
    for s in $subs; do
      name="$(resolve_submodule_name "$checkout" "$s")" \
        || die "submodule not in .gitmodules: $s (subject=$id)"
      path="$(git -C "$checkout" config -f .gitmodules --get "submodule.$name.path")"
      git -C "$checkout" submodule update --init --depth 1 -- "$path" \
        || git -C "$checkout" submodule update --init -- "$path"
    done
  else
    echo "==> no planned submodules for $id (shell only)"
  fi

  local sha
  sha="$(git -C "$checkout" rev-parse HEAD)"
  echo "    $id @ $sha ($(git -C "$checkout" rev-parse --abbrev-ref HEAD))"

  if [[ "$WRITE_PIN" -eq 1 ]]; then
    local pin="$SUBJECTS_DIR/$id/pin.json"
    # shellcheck disable=SC2086
    python3 - "$pin" "$id" "$remote" "$branch" "$sha" "$checkout" $subs <<'PY'
import json, os, subprocess, sys
from datetime import date

pin_path, sid, remote, branch, sha, checkout = sys.argv[1:7]
subs = sys.argv[7:]
sub_pins = {}
for s in subs:
    path = s
    try:
        out = subprocess.check_output(
            [
                "git", "-C", checkout, "config", "-f", ".gitmodules",
                "--get", f"submodule.{s}.path",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            path = out
    except subprocess.CalledProcessError:
        pass
    full = os.path.join(checkout, path)
    git_dir = os.path.join(full, ".git")
    if os.path.isdir(git_dir) or os.path.isfile(git_dir):
        sub_sha = subprocess.check_output(
            ["git", "-C", full, "rev-parse", "HEAD"], text=True
        ).strip()
        sub_pins[path] = sub_sha
    else:
        sub_pins[path] = None

doc = {
    "subject": sid,
    "remote": remote,
    "branch": branch,
    "sha": sha,
    "pinned_at": date.today().isoformat(),
    "submodules": sub_pins,
}
with open(pin_path, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=2)
    f.write("\n")
print(f"    wrote {pin_path}")
PY
  fi
}

for id in $TARGETS; do
  sync_one "$id"
done

echo "done."
