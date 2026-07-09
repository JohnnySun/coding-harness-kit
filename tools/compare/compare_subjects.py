#!/usr/bin/env python3
"""Compare harness snapshots (or live ready subjects) across four layers."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "lib"))
sys.path.insert(0, str(ROOT / "tools" / "sync" / "lib"))
from planned_submodules import list_subjects  # noqa: E402
from subject_ready import harness_ready, load_manifest_text, require_ready  # noqa: E402

LAYERS = ("constraints", "gates", "feedback", "evolution")


def latest_snapshot(sid: str) -> Path | None:
    snap = ROOT / "snapshots"
    if not snap.is_dir():
        return None
    cands = sorted(
        [p for p in snap.iterdir() if p.is_dir() and p.name.startswith(f"{sid}@")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return cands[0] if cands else None


def inventory(snap: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for layer in LAYERS:
        base = snap / layer
        files: list[str] = []
        if base.is_dir():
            for p in sorted(base.rglob("*")):
                if p.is_file() or p.is_symlink():
                    files.append(str(p.relative_to(base)))
        out[layer] = files
    return out


def score_layers(inv: dict[str, list[str]]) -> dict[str, int]:
    """0–2 per layer: empty=0, thin=1, substantial=2."""
    scores = {}
    for layer, files in inv.items():
        real = [f for f in files if not f.endswith("README.md") and not f.startswith("_missing_")]
        if not real:
            scores[layer] = 0
        elif len(real) < 3:
            scores[layer] = 1
        else:
            scores[layer] = 2
    return scores


def compare(sids: list[str]) -> str:
    lines: list[str] = ["# Harness compare", ""]
    rows = []
    for sid in sids:
        require_ready(sid)
        snap = latest_snapshot(sid)
        if not snap:
            print(
                f"error: no snapshot for {sid}; run: python3 tools/import/import_subject.py {sid}",
                file=sys.stderr,
            )
            raise SystemExit(1)
        man = json.loads((snap / "manifest.json").read_text(encoding="utf-8"))
        inv = inventory(snap)
        sc = score_layers(inv)
        rows.append((sid, man, inv, sc, snap))

    lines.append("| subject | shell_sha | constraints | gates | feedback | evolution | total |")
    lines.append("|---|---|---|---|---|---|---|")
    for sid, man, inv, sc, snap in rows:
        total = sum(sc.values())
        lines.append(
            f"| {sid} | `{man['shell_sha'][:12]}` | {sc['constraints']} | {sc['gates']} | "
            f"{sc['feedback']} | {sc['evolution']} | **{total}/8** |"
        )
    lines.append("")
    for sid, man, inv, sc, snap in rows:
        lines.append(f"## {sid}")
        lines.append(f"- snapshot: `{snap.relative_to(ROOT)}`")
        lines.append(f"- extras_present: {man.get('extras_present')}")
        lines.append(f"- harness_paths: {len(man.get('harness_paths') or [])}")
        for layer in LAYERS:
            lines.append(f"- **{layer}** ({sc[layer]}/2): {len(inv[layer])} files")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("subjects", nargs="*", help="subject ids (default: all)")
    ap.add_argument("-o", "--out", type=Path, help="write report under comparisons/")
    args = ap.parse_args()
    text = load_manifest_text()
    sids = args.subjects or list_subjects(text)
    body = compare(sids)
    if args.out:
        out = args.out if args.out.is_absolute() else ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body + "\n", encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(body)


if __name__ == "__main__":
    main()
