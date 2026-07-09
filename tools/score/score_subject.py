#!/usr/bin/env python3
"""Score a subject's harness snapshot (four layers 0–2). Requires harness-ready."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "compare"))
sys.path.insert(0, str(ROOT / "tools" / "lib"))
from compare_subjects import inventory, latest_snapshot, score_layers  # noqa: E402
from subject_ready import require_ready  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("subject")
    ap.add_argument(
        "-o",
        "--out",
        type=Path,
        help="write JSON+md under comparisons/ (default: comparisons/<id>-score-<date>)",
    )
    args = ap.parse_args()
    sid = args.subject
    require_ready(sid)
    snap = latest_snapshot(sid)
    if not snap:
        print(
            f"error: no snapshot; run python3 tools/import/import_subject.py {sid}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    inv = inventory(snap)
    sc = score_layers(inv)
    total = sum(sc.values())
    doc = {
        "subject": sid,
        "snapshot": str(snap.relative_to(ROOT)),
        "scored_at": date.today().isoformat(),
        "layers": sc,
        "total": total,
        "max": 8,
        "note": "Surface inventory heuristic — not a substitute for harness-builder qualitative review.",
    }
    out_base = args.out
    if out_base is None:
        out_base = ROOT / "comparisons" / f"{sid}-score-{date.today().isoformat()}"
    elif not out_base.is_absolute():
        out_base = ROOT / out_base
    out_base.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_base.with_suffix(".json") if out_base.suffix == "" else out_base
    if json_path.suffix != ".json":
        json_path = Path(str(out_base) + ".json")
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    md = [
        f"# Score: {sid}",
        "",
        f"Total: **{total}/8**",
        "",
        "| layer | score |",
        "|---|---|",
    ]
    for k, v in sc.items():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append(f"Snapshot: `{snap.relative_to(ROOT)}`")
    md.append("")
    md.append(doc["note"])
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {json_path.relative_to(ROOT)} ({total}/8)")
    print(f"wrote {md_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
