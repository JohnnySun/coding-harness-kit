#!/usr/bin/env python3
"""Aggregate docs/harness ledgers into a weekly report (環3 輕量版)."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "docs" / "harness" / "gate-events.jsonl"
INBOX = ROOT / "docs" / "harness" / "retro-inbox.md"
GATES = ROOT / "docs" / "harness" / "gates.json"
WO = ROOT / "docs" / "harness" / "work-orders.md"
OUT_DIR = ROOT / "docs" / "harness" / "reports"


def load_events(since: datetime) -> list[dict]:
    if not EVENTS.is_file():
        return []
    rows = []
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = row.get("ts")
        if ts:
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                continue
            if t >= since:
                rows.append(row)
        else:
            rows.append(row)
    return rows


def inbox_new_count() -> int:
    if not INBOX.is_file():
        return 0
    text = INBOX.read_text(encoding="utf-8")
    return text.count("status: new") + text.count("`new`")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()
    since = datetime.now(tz=None) - timedelta(days=args.days)  # local naive window
    events = load_events(since)
    counts = Counter(e.get("event", "unknown") for e in events)
    today = date.today().isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{today}.md"
    debts = []
    if GATES.is_file():
        g = json.loads(GATES.read_text(encoding="utf-8"))
        debts = g.get("debts") or []

    lines = [
        f"# Harness weekly report — {today}",
        "",
        f"Window: last {args.days} days.",
        "",
        "## Gate events",
        "",
    ]
    if not counts:
        lines.append("_No events in window._")
    else:
        lines.append("| event | count |")
        lines.append("|---|---|")
        for k, v in counts.most_common():
            lines.append(f"| {k} | {v} |")
    lines += [
        "",
        "## Inbox backlog",
        "",
        f"Approx `status: new` markers in retro-inbox: **{inbox_new_count()}**",
        "",
        "## Debts (gates.json)",
        "",
    ]
    if not debts:
        lines.append("_None._")
    else:
        for d in debts:
            lines.append(f"- `{d.get('id')}` ({d.get('class')}): {d.get('reason')}")
    lines += [
        "",
        "## Consumption protocol",
        "",
        "同一 session 必須逐項歸因 → 工單 / ratchet 收緊 / 「不處理+原因」。",
        "散文建議不是合法產出。",
        "",
        f"Work orders: `{WO.relative_to(ROOT)}`",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
