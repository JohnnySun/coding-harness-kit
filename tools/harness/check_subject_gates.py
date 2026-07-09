#!/usr/bin/env python3
"""Run a subject's declared trusted_suite against a checkout/fixture root.

Protocol (subject-agnostic):
  Registry (subjects/manifest*.yaml) may declare per subject:
    trusted_suite: "<command run with cwd = subject root>"
    fixture_root: "<repo-relative path>"   # public in-repo stand-in (CI)

Resolution of subject root (rev.2 — first hit wins):
  1. --root CLI override (must stay inside this repo)
  2. If --fixture (or public-suite mode): fixture_root (required)
  3. Else if subjects/<id>/checkout exists: use checkout (prefer over fixture)
  4. Else if fixture_root set: use fixture
  5. Else skip

No trusted_suite → skip (exit 0 for that subject, message on stderr).
Does not clone remotes. Does not read pin.json.

Trust boundary: trusted_suite is a shell command from committed example YAML
or an operator-controlled local manifest — never a remote-fetched registry.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "sync" / "lib"))
from planned_submodules import list_subjects, subject_scalar  # noqa: E402


def _subject_block(text: str, sid: str) -> str:
    pat = re.compile(rf"^  {re.escape(sid)}:\s*$", re.M)
    m = pat.search(text)
    if not m:
        raise SystemExit(f"subject not found: {sid}")
    rest = text[m.end() :]
    end_m = re.search(r"^  [a-zA-Z0-9_-]+:\s*$", rest, re.M)
    return rest[: end_m.start()] if end_m else rest


def optional_scalar(manifest_text: str, sid: str, field: str) -> str | None:
    block = _subject_block(manifest_text, sid)
    for line in block.splitlines():
        m = re.match(rf"^\s+{re.escape(field)}:\s*(.+?)\s*$", line)
        if m:
            val = m.group(1).strip().strip("\"'")
            if val in (">", "|", "", "null", "~"):
                return None
            return val
    return None


def _require_inside_repo(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SystemExit(f"{label} escapes repo: {path}") from exc
    return resolved


def _fixture_path(sid: str, manifest_text: str) -> Path | None:
    fixture = optional_scalar(manifest_text, sid, "fixture_root")
    if not fixture:
        return None
    cand = _require_inside_repo(ROOT / fixture, f"{sid}: fixture_root")
    if not cand.is_dir():
        raise SystemExit(f"{sid}: fixture_root missing: {fixture}")
    return cand


def resolve_subject_root(
    sid: str,
    manifest_text: str,
    root_override: Path | None,
    *,
    force_fixture: bool = False,
) -> Path | None:
    if root_override is not None:
        return _require_inside_repo(root_override, f"{sid}: --root")

    if force_fixture:
        fixture = _fixture_path(sid, manifest_text)
        if fixture is None:
            raise SystemExit(f"{sid}: --fixture requires fixture_root in registry")
        return fixture

    local = ROOT / "subjects" / sid / "checkout"
    if local.is_dir():
        return local.resolve()

    return _fixture_path(sid, manifest_text)


def run_subject_gates(
    sid: str,
    manifest_text: str,
    root_override: Path | None = None,
    *,
    force_fixture: bool = False,
) -> int:
    suite = optional_scalar(manifest_text, sid, "trusted_suite")
    if not suite:
        print(f"skip  [{sid}] no trusted_suite declared", file=sys.stderr)
        return 0
    subject_root = resolve_subject_root(
        sid, manifest_text, root_override, force_fixture=force_fixture
    )
    if subject_root is None:
        print(f"skip  [{sid}] no fixture_root / checkout", file=sys.stderr)
        return 0
    print(f"== subject gates [{sid}] @ {subject_root}")
    print(f"   trusted_suite: {suite}")
    proc = subprocess.run(
        suite,
        shell=True,
        cwd=str(subject_root),
        text=True,
    )
    if proc.returncode != 0:
        print(f"FAIL  [{sid}] trusted_suite exit {proc.returncode}", file=sys.stderr)
        return 1
    print(f"ok    [{sid}] trusted_suite")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="registry YAML (default: example, else local)",
    )
    ap.add_argument("--subject", help="single subject id")
    ap.add_argument("--all", action="store_true", help="all subjects in manifest")
    ap.add_argument("--root", type=Path, help="override subject root (must be inside repo)")
    ap.add_argument(
        "--fixture",
        action="store_true",
        help="force fixture_root (public suite / CI); ignore checkout even if present",
    )
    args = ap.parse_args(argv)

    if args.manifest is not None:
        man_path = args.manifest
    elif (ROOT / "subjects" / "manifest.example.yaml").is_file():
        man_path = ROOT / "subjects" / "manifest.example.yaml"
        if os.environ.get("HARNESS_SUBJECT_MANIFEST") == "local":
            local = ROOT / "subjects" / "manifest.yaml"
            if local.is_file():
                man_path = local
    else:
        man_path = ROOT / "subjects" / "manifest.yaml"
    if not man_path.is_file():
        print(f"missing manifest: {man_path}", file=sys.stderr)
        return 2

    text = man_path.read_text(encoding="utf-8")
    if args.subject:
        subjects = [args.subject]
    elif args.all:
        subjects = list_subjects(text)
    else:
        ap.error("need --subject or --all")

    force_fixture = bool(args.fixture)
    rc = 0
    for sid in subjects:
        try:
            subject_scalar(text, sid, "remote")
        except SystemExit as e:
            print(str(e), file=sys.stderr)
            return 2
        root = args.root if len(subjects) == 1 else None
        if run_subject_gates(sid, text, root, force_fixture=force_fixture) != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
