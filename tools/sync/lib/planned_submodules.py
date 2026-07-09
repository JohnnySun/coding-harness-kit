#!/usr/bin/env python3
"""Planned submodule paths for a subject (default_submodules ∪ --with).

Single implementation used by sync-subjects.sh and the trusted suite.
No network / no clone — pure manifest parse.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _subject_block(text: str, sid: str) -> str:
    pat = re.compile(rf"^  {re.escape(sid)}:\s*$", re.M)
    m = pat.search(text)
    if not m:
        raise SystemExit(f"subject not found: {sid}")
    rest = text[m.end() :]
    end_m = re.search(r"^  [a-zA-Z0-9_-]+:\s*$", rest, re.M)
    return rest[: end_m.start()] if end_m else rest


def default_submodules(manifest_text: str, sid: str) -> list[str]:
    block = _subject_block(manifest_text, sid)
    for i, line in enumerate(block.splitlines()):
        if re.match(r"^\s+default_submodules:\s*\[\s*\]\s*$", line):
            return []
        if re.match(r"^\s+default_submodules:\s*$", line):
            out: list[str] = []
            for cont in block.splitlines()[i + 1 :]:
                im = re.match(r"^\s+-\s+(\S+)\s*$", cont)
                if not im:
                    break
                out.append(im.group(1))
            return out
    return []


def planned_submodules(
    manifest_text: str,
    sid: str,
    with_extra: list[str] | None = None,
) -> list[str]:
    paths = list(default_submodules(manifest_text, sid))
    for e in with_extra or []:
        e = e.strip()
        if e and e not in paths:
            paths.append(e)
    return paths


def list_subjects(manifest_text: str) -> list[str]:
    in_subjects = False
    out: list[str] = []
    for line in manifest_text.splitlines():
        if re.match(r"^subjects:\s*$", line):
            in_subjects = True
            continue
        if in_subjects:
            if re.match(r"^\S", line) and not line.startswith("#"):
                break
            m = re.match(r"^  ([a-zA-Z0-9_-]+):\s*$", line)
            if m:
                out.append(m.group(1))
    return out


def subject_scalar(manifest_text: str, sid: str, field: str) -> str:
    block = _subject_block(manifest_text, sid)
    for line in block.splitlines():
        m = re.match(rf"^\s+{re.escape(field)}:\s*(.+?)\s*$", line)
        if m:
            val = m.group(1).strip().strip("\"'")
            if val in (">", "|"):
                continue
            return val
    raise SystemExit(f"field not found: {sid}.{field}")


def harness_paths(manifest_text: str, sid: str) -> list[str]:
    block = _subject_block(manifest_text, sid)
    for i, line in enumerate(block.splitlines()):
        if re.match(r"^\s+harness_paths:\s*$", line):
            out: list[str] = []
            for cont in block.splitlines()[i + 1 :]:
                im = re.match(r"^\s+-\s+(\S+)\s*$", cont)
                if not im:
                    break
                out.append(im.group(1))
            return out
    raise SystemExit(f"harness_paths not found: {sid}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("subject")
    ap.add_argument(
        "--with",
        dest="with_extra",
        default="",
        help="comma-separated extra submodule paths",
    )
    args = ap.parse_args()
    text = args.manifest.read_text(encoding="utf-8")
    extras = [x for x in args.with_extra.split(",") if x.strip()]
    for p in planned_submodules(text, args.subject, extras):
        print(p)


if __name__ == "__main__":
    main()
