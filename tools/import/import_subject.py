#!/usr/bin/env python3
"""Import subject harness surface → snapshots/<id>@<sha>/ (design §5)."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "lib"))
sys.path.insert(0, str(ROOT / "tools" / "sync" / "lib"))
from planned_submodules import harness_paths, list_subjects  # noqa: E402
from subject_ready import (  # noqa: E402
    extras_present,
    load_manifest_text,
    require_ready,
)

LAYERS = ("constraints", "gates", "feedback", "evolution")


def classify(rel: str) -> str:
    name = rel.lower()
    base = Path(rel).name.lower()
    if base in {"claude.md", "agents.md", "design.md", "readme.md"}:
        return "constraints"
    if "skill" in name or name.startswith(".cursor") or name.startswith(".agents"):
        return "constraints"
    if "hook" in name or name.endswith("hooks.json") or "ratchet" in name:
        return "gates"
    if name.startswith("scripts/harness") or name == "agent-kit/hooks":
        return "gates"
    if "harness" in name and ("inbox" in name or "ledger" in name or "deviation" in name):
        return "feedback"
    if "retro" in name or "work-order" in name or "report" in name:
        return "evolution"
    if name.startswith("docs/harness"):
        return "feedback"
    if name.startswith("docs/specs"):
        return "evolution"
    if name.startswith("agent-kit"):
        return "constraints"
    return "constraints"


def copy_path(src: Path, dest: Path) -> None:
    if not src.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        (dest.parent / f"_missing_{dest.name}.txt").write_text(
            f"missing at import: {src}\n", encoding="utf-8"
        )
        return
    if src.is_symlink():
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        dest.symlink_to(src.resolve())
        return
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(
            src,
            dest,
            symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git",
                "node_modules",
                "__pycache__",
                "*.pyc",
                "checkout",
            ),
        )
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def import_subject(sid: str) -> Path:
    require_ready(sid)
    text = load_manifest_text()
    checkout = ROOT / "subjects" / sid / "checkout"
    pin = json.loads((ROOT / "subjects" / sid / "pin.json").read_text(encoding="utf-8"))
    shell_sha = pin["sha"]
    paths = harness_paths(text, sid)
    out = ROOT / "snapshots" / f"{sid}@{shell_sha[:12]}"
    if out.exists():
        shutil.rmtree(out)
    for layer in LAYERS:
        (out / layer).mkdir(parents=True)

    for rel in paths:
        src = checkout / rel
        layer = classify(rel)
        # preserve relative path under layer
        dest = out / layer / rel
        copy_path(src, dest)

    # ensure layer READMEs so empty dirs stay meaningful
    for layer in LAYERS:
        readme = out / layer / "README.md"
        if not readme.exists():
            readme.write_text(
                f"# {layer}\n\nImported harness surface for `{sid}`.\n",
                encoding="utf-8",
            )

    man = {
        "schema_version": 1,
        "subject": sid,
        "shell_sha": shell_sha,
        "submodules": pin.get("submodules") or {},
        "harness_paths": paths,
        "imported_at": date.today().isoformat(),
        "extras_present": extras_present(checkout, text, sid),
    }
    (out / "manifest.json").write_text(
        json.dumps(man, indent=2) + "\n", encoding="utf-8"
    )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("subject", nargs="?", help="subject id (default: all ready)")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    text = load_manifest_text()
    targets = list_subjects(text) if args.all or not args.subject else [args.subject]
    for sid in targets:
        out = import_subject(sid)
        print(f"imported {sid} → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
