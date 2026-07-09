#!/usr/bin/env python3
"""Shared subject readiness + manifest helpers for import/compare/score."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "sync" / "lib"))
from planned_submodules import (  # noqa: E402
    default_submodules,
    harness_paths,
    list_subjects,
)

MANIFEST = ROOT / "subjects" / "manifest.yaml"


def load_manifest_text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def git_head(cwd: Path) -> str | None:
    if not (cwd / ".git").exists() and not (cwd / ".git").is_file():
        # .git file for submodules
        if not (cwd / ".git").exists():
            return None
    r = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
    )
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def submodule_present(checkout: Path, rel: str) -> bool:
    path = checkout / rel
    if not path.is_dir():
        return False
    git_marker = path / ".git"
    if not (git_marker.is_file() or git_marker.is_dir()):
        return False
    skills_like = rel == ".claude" or "skills" in rel.split("/")
    if skills_like:
        has_skill = any(path.rglob("SKILL.md"))
        has_hooks = (path / "hooks").exists() or (path / "settings.json").exists()
        return has_skill or has_hooks
    entries = [p for p in path.iterdir() if p.name != ".git"]
    return bool(entries)


def extras_present(checkout: Path, text: str, sid: str) -> bool:
    """Heuristic: any submodule path under checkout that is not in defaults and has .git."""
    defaults = set(default_submodules(text, sid))
    gitmodules = checkout / ".gitmodules"
    if not gitmodules.is_file():
        return False
    # parse paths from .gitmodules
    paths: list[str] = []
    for line in gitmodules.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("path = "):
            paths.append(line.split("=", 1)[1].strip())
    for p in paths:
        if p in defaults:
            continue
        sub = checkout / p
        if (sub / ".git").exists() or (sub / ".git").is_file():
            # only count if actually populated
            try:
                if any(sub.iterdir()):
                    return True
            except OSError:
                pass
    return False


def harness_ready(sid: str, text: str | None = None) -> tuple[bool, str]:
    """Return (ok, reason). Does not honor HARNESS_ALLOW_DRIFT."""
    text = text or load_manifest_text()
    if sid not in list_subjects(text):
        return False, f"unknown subject: {sid}"
    checkout = ROOT / "subjects" / sid / "checkout"
    if not (checkout / ".git").exists():
        return False, f"{sid}: checkout absent"
    pin_path = ROOT / "subjects" / sid / "pin.json"
    if not pin_path.is_file():
        return False, f"{sid}: missing pin.json"
    pin = json.loads(pin_path.read_text(encoding="utf-8"))
    head = git_head(checkout)
    if not head:
        return False, f"{sid}: cannot read HEAD"
    if pin.get("sha") != head:
        return False, f"{sid}: drifted (pin={pin.get('sha')} HEAD={head})"
    sub_pins = pin.get("submodules") or {}
    for rel in default_submodules(text, sid):
        expected = sub_pins.get(rel)
        if expected is None:
            return False, f"{sid}: pin.submodules[{rel!r}] null/missing"
        if not submodule_present(checkout, rel):
            return False, f"{sid}: default submodule not present: {rel}"
        sub_head = git_head(checkout / rel)
        if sub_head != expected:
            return False, f"{sid}: submodule pin drift {rel}"
    return True, "harness-ready"


def require_ready(sid: str) -> None:
    ok, reason = harness_ready(sid)
    if not ok:
        print(f"error: subject not harness-ready: {reason}", file=sys.stderr)
        print(
            "hint: bash tools/sync/sync-subjects.sh {sid} --pin".format(sid=sid),
            file=sys.stderr,
        )
        raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    """CLI for local absorb readiness (not the public trusted suite)."""
    import argparse

    ap = argparse.ArgumentParser(
        description=(
            "Check harness-ready for local subjects (pin/checkout). "
            "Not part of the public trusted suite."
        )
    )
    ap.add_argument("subject", nargs="?", help="subject id")
    ap.add_argument("--all", action="store_true", help="all subjects in local manifest")
    args = ap.parse_args(argv)

    if not MANIFEST.is_file():
        print(
            f"error: missing {MANIFEST} (copy from subjects/manifest.example.yaml)",
            file=sys.stderr,
        )
        return 2

    text = load_manifest_text()
    if args.subject:
        subjects = [args.subject]
    elif args.all:
        subjects = list_subjects(text)
    else:
        ap.error("need subject id or --all")

    rc = 0
    for sid in subjects:
        ok, reason = harness_ready(sid, text)
        if ok:
            print(f"ok    [{sid}] {reason}")
        else:
            print(f"FAIL  [{sid}] {reason}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
