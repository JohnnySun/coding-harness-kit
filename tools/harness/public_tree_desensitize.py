"""Scan public-tree file contents for private absorb leaks.

Complements path-based F5+ (gitignore / pre-commit path deny): this catches
sensitive *text* inside otherwise-public files (docs, tools, agent-kit templates).

Always-on patterns (CI-safe, no private manifest required):
  - absolute home paths (/Users/<name>/…, /home/<name>/…)
  - absolute …/subjects/<id>/checkout paths

When local subjects/manifest.yaml exists, also ban that registry's subject ids
and remotes from appearing in public tracked/staged content.

Employer / org brand names are an *AI* constraint (AGENTS.md), not a string
scanner — embedding a ban-list token in this gate would reintroduce the leak.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Text / config surfaces we care about. Binary and lock noise stay out.
SCAN_SUFFIXES = {
    ".md",
    ".mjs",
    ".js",
    ".cjs",
    ".ts",
    ".tsx",
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".csv",
}

# Paths that are private absorb (never scanned as "public") or not our SSOT.
SKIP_PREFIXES = (
    "subjects/",
    "snapshots/",
    "comparisons/",
    "docs/harness/reports/",
    "docs/harness/gate-events.jsonl",
    ".cursor/",
    ".agents/",
    ".claude/",
    ".codex/",
    "node_modules/",
    "agent-kit/skills/",  # submodule; content owned upstream
)

# Public example registry is allowed to contain example remotes only.
ALWAYS_PUBLIC = frozenset({"subjects/manifest.example.yaml"})

HOME_ABS_RE = re.compile(
    r"(?:/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+)"
)

# Absolute checkout bodies (home + subjects/<id>/checkout).
ABS_CHECKOUT_RE = re.compile(
    r"(?:/Users/|/home/)[^\s\"'`]+/subjects/[A-Za-z0-9._-]+/checkout\b"
)

REMOTE_LINE_RE = re.compile(
    r"^\s*remote:\s*(.+?)\s*$",
    re.MULTILINE,
)
SUBJECT_KEY_RE = re.compile(
    r"^  ([A-Za-z0-9][A-Za-z0-9._-]*)\s*:\s*$",
    re.MULTILINE,
)


def is_scannable_path(rel: str) -> bool:
    if rel in ALWAYS_PUBLIC:
        return True
    if any(rel == p or rel.startswith(p) for p in SKIP_PREFIXES):
        return False
    # Never treat private manifest as public content.
    if rel == "subjects/manifest.yaml":
        return False
    suffix = Path(rel).suffix.lower()
    if suffix and suffix not in SCAN_SUFFIXES:
        return False
    # Extensionless scripts under tools/ are rare; skip unknown binaries.
    if not suffix and not rel.startswith("tools/"):
        return False
    return True


def load_private_registry_tokens(manifest: Path) -> tuple[set[str], set[str]]:
    """Return (subject_ids, remotes) from a local private manifest, if present."""
    if not manifest.is_file():
        return set(), set()
    text = manifest.read_text(encoding="utf-8")
    ids = {m.group(1) for m in SUBJECT_KEY_RE.finditer(text)}
    remotes: set[str] = set()
    for m in REMOTE_LINE_RE.finditer(text):
        remote = m.group(1).strip().strip("\"'")
        if remote:
            remotes.add(remote)
    # Drop YAML structural false positives under non-subject keys.
    ids.discard("subjects")
    return ids, remotes


def find_leaks_in_text(
    text: str,
    *,
    subject_ids: set[str] | None = None,
    remotes: set[str] | None = None,
) -> list[str]:
    """Return human-readable leak descriptions for one file body."""
    hits: list[str] = []
    if ABS_CHECKOUT_RE.search(text):
        hits.append("absolute subjects/<id>/checkout path")
    for m in HOME_ABS_RE.finditer(text):
        hits.append(f"absolute home path ({m.group(0)})")
        break  # one sample is enough
    for remote in sorted(remotes or ()):
        if remote and remote in text:
            hits.append(f"private subject remote ({remote})")
    for sid in sorted(subject_ids or ()):
        # Word-ish boundary: avoid matching inside longer tokens.
        if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(sid)}(?![A-Za-z0-9_-])", text):
            hits.append(f"private subject id ({sid})")
    return hits


def iter_git_tracked_files(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [p for p in proc.stdout.decode("utf-8", errors="replace").split("\0") if p]


def iter_staged_files(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(root), "diff", "--cached", "--name-only", "-z"],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [p for p in proc.stdout.decode("utf-8", errors="replace").split("\0") if p]


def scan_paths(
    root: Path,
    rel_paths: list[str],
    *,
    subject_ids: set[str] | None = None,
    remotes: set[str] | None = None,
) -> list[tuple[str, str]]:
    """Return list of (rel_path, leak_description)."""
    findings: list[tuple[str, str]] = []
    for rel in rel_paths:
        if not is_scannable_path(rel):
            continue
        path = root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for hit in find_leaks_in_text(
            text, subject_ids=subject_ids, remotes=remotes
        ):
            findings.append((rel, hit))
    return findings


def scan_public_tree(
    root: Path | None = None,
    *,
    paths: list[str] | None = None,
    private_manifest: Path | None = None,
) -> list[tuple[str, str]]:
    root = root or ROOT
    manifest = private_manifest or (root / "subjects" / "manifest.yaml")
    subject_ids, remotes = load_private_registry_tokens(manifest)
    if paths is None:
        paths = iter_git_tracked_files(root)
        # Also include untracked public files that are part of the working tree
        # beat (so pre-commit / local suite catch leaks before first add).
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0:
            extra = [
                p
                for p in proc.stdout.decode("utf-8", errors="replace").split("\0")
                if p
            ]
            paths = list(dict.fromkeys([*paths, *extra]))
    return scan_paths(
        root, paths, subject_ids=subject_ids, remotes=remotes
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    staged_only = "--staged" in argv
    root = ROOT
    if staged_only:
        paths = iter_staged_files(root)
        findings = scan_public_tree(root, paths=paths)
    else:
        findings = scan_public_tree(root)
    if not findings:
        print("ok    [public-tree-desensitize] no private content in public tree")
        return 0
    print("FAIL  [public-tree-desensitize] private content in public tree:", file=sys.stderr)
    for rel, hit in findings:
        print(f"  - {rel}: {hit}", file=sys.stderr)
    print(
        "  Desensitize to example/relative wording, or keep under subjects/** (gitignored).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
