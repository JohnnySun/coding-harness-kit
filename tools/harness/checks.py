#!/usr/bin/env python3
"""Harness-dev *public* trusted suite checks.

Decoupled from private subjects/** state (pin/checkout/snapshot contents).
Subject gate execution uses the protocol checker + in-repo fixtures only.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "sync" / "lib"))
sys.path.insert(0, str(ROOT / "tools" / "harness"))
from planned_submodules import (  # noqa: E402
    default_submodules,
    harness_paths,
    list_subjects,
    planned_submodules,
    subject_scalar,
)
from check_subject_gates import optional_scalar  # noqa: E402

MANIFEST_EXAMPLE = ROOT / "subjects" / "manifest.example.yaml"
SYNC_SH = ROOT / "tools" / "sync" / "sync-subjects.sh"
PLANNED_LIB = ROOT / "tools" / "sync" / "lib" / "planned_submodules.py"
DESIGN = ROOT / "docs" / "harness" / "design.md"
CHECK_SUBJECT_GATES = ROOT / "tools" / "harness" / "check_subject_gates.py"

PRIVATE_TREE_RULES = ("subjects/", "snapshots/", "comparisons/")

PLATFORM_SKILL_ROOTS = [
    ROOT / ".cursor" / "skills",
    ROOT / ".agents" / "skills",
    ROOT / ".claude" / "skills",
    ROOT / ".codex" / "skills",
]

LEDGER_FILES = {
    "gate-events": ROOT / "docs" / "harness" / "gate-events.jsonl",
    "retro-inbox": ROOT / "docs" / "harness" / "retro-inbox.md",
    "gates.json": ROOT / "docs" / "harness" / "gates.json",
    "deviation-log": ROOT / "docs" / "harness" / "deviation-log.md",
    "work-orders": ROOT / "docs" / "harness" / "work-orders.md",
}

FAILS: list[str] = []


def fail(check: str, msg: str) -> None:
    FAILS.append(f"[{check}] {msg}")
    print(f"FAIL  [{check}] {msg}", file=sys.stderr)


def ok(check: str, msg: str = "") -> None:
    suffix = f" — {msg}" if msg else ""
    print(f"ok    [{check}]{suffix}")


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
    )


def _optional_field(text: str, sid: str, field: str) -> str | None:
    return optional_scalar(text, sid, field)


def check_manifest_schema(text: str) -> None:
    cid = "manifest-schema"
    for sid in list_subjects(text):
        for field in ("remote", "default_branch"):
            try:
                subject_scalar(text, sid, field)
            except SystemExit as e:
                fail(cid, str(e))
                return
        try:
            hp = harness_paths(text, sid)
            if not hp:
                fail(cid, f"{sid}: harness_paths empty")
                return
        except SystemExit as e:
            fail(cid, str(e))
            return
        default_submodules(text, sid)
        suite = _optional_field(text, sid, "trusted_suite")
        fixture = _optional_field(text, sid, "fixture_root")
        if suite and not fixture:
            # Public example subjects that declare a suite must be CI-runnable via fixture.
            fail(cid, f"{sid}: trusted_suite set but fixture_root missing (public protocol)")
            return
        if fixture:
            fr = (ROOT / fixture).resolve()
            try:
                fr.relative_to(ROOT.resolve())
            except ValueError:
                fail(cid, f"{sid}: fixture_root escapes repo")
                return
            if not fr.is_dir():
                fail(cid, f"{sid}: fixture_root not a directory: {fixture}")
                return
    bad = "subjects:\n  x:\n    default_branch: main\n    default_submodules: []\n    harness_paths:\n      - A\n"
    try:
        subject_scalar(bad, "x", "remote")
        fail(cid, "negative fixture should miss remote")
    except SystemExit:
        pass
    ok(cid, f"{len(list_subjects(text))} subjects (public example)")


def submodule_present(checkout: Path, rel: str) -> tuple[bool, str]:
    """§2.1 predicate (fixture-only; not applied to private checkouts in public suite)."""
    path = checkout / rel
    if not path.is_dir():
        return False, f"missing dir {rel}"
    git_marker = path / ".git"
    if not (git_marker.is_file() or git_marker.is_dir()):
        return False, f"{rel}: no .git (not a checkout/submodule)"
    skills_like = rel == ".claude" or "skills" in rel.split("/")
    if skills_like:
        has_skill = any(path.rglob("SKILL.md"))
        has_hooks = (path / "hooks").exists() or (path / "settings.json").exists()
        if not (has_skill or has_hooks):
            return False, f"{rel}: no SKILL.md / hooks / settings.json"
    else:
        entries = [p for p in path.iterdir() if p.name != ".git"]
        if not entries:
            return False, f"{rel}: empty"
    return True, "ok"


def check_submodule_fixture() -> None:
    """Forced fixture: empty .claude must fail predicate; with SKILL.md pass."""
    cid = "default-submodules-present"
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        empty = base / "empty" / ".claude"
        empty.mkdir(parents=True)
        (empty / ".git").write_text("gitdir: /tmp/fake\n", encoding="utf-8")
        good, reason = submodule_present(base / "empty", ".claude")
        if good:
            fail(cid, "fixture empty .claude should be RED")
        else:
            ok(cid, f"fixture empty→red ({reason})")

        filled = base / "filled" / ".claude"
        filled.mkdir(parents=True)
        (filled / ".git").write_text("gitdir: /tmp/fake\n", encoding="utf-8")
        skill = filled / "skills" / "x"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# x\n", encoding="utf-8")
        good2, _ = submodule_present(base / "filled", ".claude")
        if not good2:
            fail(cid, "fixture with SKILL.md should be GREEN")
        else:
            ok(cid, "fixture skill→green")


def check_client_trees_ignored() -> None:
    """Platform client trees must be gitignored (install-generated, never committed)."""
    cid = "client-trees-ignored"
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for name in (".agents/", ".claude/", ".codex/", ".cursor/"):
        if name not in gi:
            fail(cid, f".gitignore must ignore {name}")
            return
    # Must not be tracked in the index
    proc = run(["git", "ls-files", ".agents", ".claude", ".codex", ".cursor"])
    tracked = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if tracked:
        fail(cid, f"client trees tracked in git (run git rm --cached): {tracked[:5]}")
        return
    ok(cid, "platform client trees ignored + untracked")


def check_symlink_health() -> None:
    cid = "symlink-health"
    target_root = (ROOT / "agent-kit" / "skills" / "skills").resolve()
    subjects_root = (ROOT / "subjects").resolve()
    any_entry = False
    missing_roots = [r for r in PLATFORM_SKILL_ROOTS if not r.is_dir()]
    if len(missing_roots) == len(PLATFORM_SKILL_ROOTS):
        fail(
            cid,
            "no platform skill trees — run: "
            "for c in cursor claude codex codex-native; do "
            "CLIENT=$c bash tools/harness/agent-kit.sh install; done",
        )
        return
    for root in PLATFORM_SKILL_ROOTS:
        if not root.is_dir():
            fail(cid, f"missing {root.relative_to(ROOT)} (run agent-kit install)")
            continue
        for child in sorted(root.iterdir()):
            if child.name.startswith("."):
                continue
            any_entry = True
            if child.is_symlink():
                try:
                    resolved = child.resolve()
                except FileNotFoundError:
                    fail(cid, f"{child.relative_to(ROOT)} broken symlink")
                    continue
                if not resolved.exists():
                    fail(cid, f"{child.relative_to(ROOT)} broken → {resolved}")
                    continue
                if subjects_root in resolved.parents or resolved == subjects_root:
                    fail(cid, f"{child.relative_to(ROOT)} → subjects/** (F7)")
                    continue
                if target_root not in resolved.parents and resolved != target_root:
                    if resolved.parent != target_root:
                        fail(
                            cid,
                            f"{child.relative_to(ROOT)} → {resolved} "
                            f"(expected under {target_root})",
                        )
                        continue
                ok(cid, str(child.relative_to(ROOT)))
                continue
            if child.is_dir():
                skill_md = child / "SKILL.md"
                if not skill_md.is_file():
                    fail(cid, f"{child.relative_to(ROOT)} dir missing SKILL.md")
                    continue
                try:
                    resolved = child.resolve()
                except FileNotFoundError:
                    fail(cid, f"{child.relative_to(ROOT)} unreadable")
                    continue
                if subjects_root in resolved.parents or resolved == subjects_root:
                    fail(cid, f"{child.relative_to(ROOT)} under subjects/** (F7)")
                    continue
                ok(cid, f"{child.relative_to(ROOT)} (plugin-copy)")
                continue
            fail(cid, f"{child.relative_to(ROOT)} is not a symlink or skill dir")
    if not any_entry:
        fail(cid, "no skill entries found")


def check_no_business_default(text: str) -> None:
    cid = "no-business-default"
    sync_src = SYNC_SH.read_text(encoding="utf-8")
    if "planned_submodules" not in sync_src:
        fail(cid, "sync-subjects.sh does not reference planned_submodules lib")
        return
    if not PLANNED_LIB.is_file():
        fail(cid, f"missing {PLANNED_LIB}")
        return
    ok(cid, "sync binds planned_submodules")

    for sid in list_subjects(text):
        defaults = default_submodules(text, sid)
        planned = planned_submodules(text, sid, [])
        if set(planned) != set(defaults):
            fail(cid, f"{sid}: planned {planned} != defaults {defaults}")
        else:
            ok(cid, f"{sid}: planned ⊆ defaults ({planned or '[]'})")

    fixture = """subjects:
  demo:
    remote: x
    default_branch: main
    default_submodules:
      - .claude
    harness_paths:
      - A
"""
    planned_extra = planned_submodules(fixture, "demo", ["server"])
    if planned_extra != [".claude", "server"]:
        fail(cid, f"fixture --with unexpected: {planned_extra}")
    else:
        ok(cid, "fixture --with expands")


def check_private_gitignore() -> None:
    cid = "private-gitignore"
    gi = ROOT / ".gitignore"
    if not gi.is_file():
        fail(cid, "missing .gitignore")
        return
    text = gi.read_text(encoding="utf-8")
    for rule in PRIVATE_TREE_RULES:
        if rule not in text:
            fail(cid, f".gitignore missing {rule!r} rule")
            return
    if "manifest.example.yaml" not in text:
        fail(cid, ".gitignore must un-ignore subjects/manifest.example.yaml")
        return
    if not MANIFEST_EXAMPLE.is_file():
        fail(cid, "missing subjects/manifest.example.yaml (public registry template)")
        return
    if (ROOT / ".git").exists():
        probes_ignored = [
            ROOT / "subjects" / "manifest.yaml",
            ROOT / "subjects" / "_probe" / "checkout" / "x",
            ROOT / "snapshots" / "_probe",
            ROOT / "comparisons" / "_probe.md",
        ]
        for probe in probes_ignored:
            r = run(["git", "check-ignore", "-q", str(probe)])
            if r.returncode != 0:
                fail(cid, f"git check-ignore did not match {probe.relative_to(ROOT)}")
                return
        r_ex = run(["git", "check-ignore", "-q", str(MANIFEST_EXAMPLE)])
        if r_ex.returncode == 0:
            fail(cid, "subjects/manifest.example.yaml must NOT be gitignored")
            return
    ok(cid, "private trees ignored; example public")


def check_ledger_registry() -> None:
    cid = "ledger-registry"
    if not DESIGN.is_file():
        fail(cid, "missing design.md")
        return
    design = DESIGN.read_text(encoding="utf-8")
    for key, path in LEDGER_FILES.items():
        token = path.name
        if token not in design and key not in design:
            fail(cid, f"§9 registry missing mention of {token}")
            continue
        if not path.exists():
            fail(cid, f"registered ledger file missing: {path.relative_to(ROOT)}")
        else:
            ok(cid, str(path.relative_to(ROOT)))

    harness_docs = ROOT / "docs" / "harness"
    known = {p.name for p in LEDGER_FILES.values()}
    known.update(
        {
            "design.md",
            "hook-smoke.md",
        }
    )
    for p in harness_docs.iterdir():
        if p.is_dir() and p.name == "reports":
            continue
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.name in known:
            continue
        # Design leftovers in harness/ are placement violations (not ledgers)
        if p.name.startswith("plan-") or p.name.endswith("-plan.md"):
            fail(cid, f"design doc in docs/harness/ (move to docs/specs/): {p.name}")
            continue
        if p.suffix in {".jsonl", ".json"} or p.name.endswith("-log.md"):
            fail(cid, f"unregistered ledger-ish file: {p.name}")


def check_docs_placement() -> None:
    """Design docs land in docs/specs/; sentinels + README present; harness/ clean of plans."""
    cid = "docs-placement"
    readme = ROOT / "docs" / "README.md"
    if not readme.is_file():
        fail(cid, "missing docs/README.md (placement SSOT)")
        return
    ok(cid, "docs/README.md")

    specs = ROOT / "docs" / "specs"
    if not specs.is_dir():
        fail(cid, "missing docs/specs/")
        return
    ok(cid, "docs/specs/")

    sentinels = [
        ROOT / "specs",  # file, not directory
        ROOT / "docs" / "superpowers",
        ROOT / "docs" / "technical-design",
    ]
    for s in sentinels:
        if not s.exists():
            fail(cid, f"missing sentinel {s.relative_to(ROOT)}")
            continue
        if s.is_dir():
            fail(cid, f"sentinel must be a file, not directory: {s.relative_to(ROOT)}")
            continue
        text = s.read_text(encoding="utf-8")
        if "READ-ONLY" not in text and "Do **not**" not in text and "Do not" not in text:
            fail(cid, f"sentinel missing READ-ONLY guidance: {s.relative_to(ROOT)}")
            continue
        ok(cid, f"sentinel {s.relative_to(ROOT)}")

    harness = ROOT / "docs" / "harness"
    if harness.is_dir():
        banned_prefixes = ("plan-", "plan_review", "spec-")
        for p in harness.iterdir():
            if not p.is_file():
                continue
            name = p.name.lower()
            if name.startswith(banned_prefixes) or name.endswith("-plan.md"):
                fail(cid, f"design artifact under docs/harness/: {p.name} → move to docs/specs/")
            if "plan-review" in name and name != "hook-smoke.md":
                # allow nothing; plan-review belongs in specs/
                if name.startswith("plan-review"):
                    fail(cid, f"plan-review under docs/harness/: {p.name}")


def check_hook_wiring() -> None:
    """Hook SSOT lives under agent-kit/hooks/clients/; client trees are install output."""
    cid = "hook-wiring"
    required = [
        ROOT / "tools" / "harness" / "hook-router.mjs",
        ROOT / "tools" / "harness" / "cursor-hook.mjs",
        ROOT / "tools" / "harness" / "prompt-skill-router.mjs",
        ROOT / "tools" / "harness" / "advisor-card.mjs",
        ROOT / "tools" / "harness" / "pre-commit.sh",
        ROOT / "agent-kit" / "hooks" / "clients" / "cursor.hooks.json",
        ROOT / "agent-kit" / "hooks" / "clients" / "claude.settings.json",
        ROOT / "agent-kit" / "hooks" / "clients" / "codex.hooks.json",
        ROOT / "agent-kit" / "hooks" / "clients" / "codex.config.toml",
        CHECK_SUBJECT_GATES,
        ROOT / ".github" / "workflows" / "harness-trusted.yml",
    ]
    for p in required:
        if not p.exists():
            fail(cid, f"missing {p.relative_to(ROOT)}")
        else:
            ok(cid, str(p.relative_to(ROOT)))
    cursor = (ROOT / "agent-kit" / "hooks" / "clients" / "cursor.hooks.json").read_text(
        encoding="utf-8"
    )
    if "cursor-hook.mjs" not in cursor:
        fail(cid, "cursor.hooks.json must call cursor-hook.mjs")
    if "beforeSubmitPrompt" not in cursor or "prompt-skill-router.mjs" not in cursor:
        fail(cid, "cursor.hooks.json must wire beforeSubmitPrompt → prompt-skill-router.mjs")
    claude = (ROOT / "agent-kit" / "hooks" / "clients" / "claude.settings.json").read_text(
        encoding="utf-8"
    )
    if "hook-router.mjs" not in claude:
        fail(cid, "claude.settings.json must call hook-router.mjs")
    if "UserPromptSubmit" not in claude or "prompt-skill-router.mjs" not in claude:
        fail(cid, "claude.settings.json must wire UserPromptSubmit → prompt-skill-router.mjs")
    # Advisor card: dispatch-time tier consultation on subagent creation.
    # Claude PreToolUse matcher on Task/Agent must route to advisor-card.mjs.
    try:
        claude_cfg = json.loads(claude)
    except json.JSONDecodeError as exc:
        fail(cid, f"claude.settings.json is not valid JSON: {exc}")
        claude_cfg = {}
    pre_tool_use = claude_cfg.get("hooks", {}).get("PreToolUse", [])
    advisor_wired = any(
        "Task" in str(group.get("matcher", ""))
        and "advisor-card.mjs" in json.dumps(group.get("hooks", []))
        for group in pre_tool_use
    )
    if not advisor_wired:
        fail(cid, "claude.settings.json must wire PreToolUse(Task) → advisor-card.mjs")
    codex_hooks = (ROOT / "agent-kit" / "hooks" / "clients" / "codex.hooks.json").read_text(
        encoding="utf-8"
    )
    if "hook-router.mjs" not in codex_hooks:
        fail(cid, "codex.hooks.json must call hook-router.mjs")
    if "UserPromptSubmit" not in codex_hooks or "prompt-skill-router.mjs" not in codex_hooks:
        fail(cid, "codex.hooks.json must wire UserPromptSubmit → prompt-skill-router.mjs")
    # Advisor card (mechanism B, degraded): Codex has no PreToolUse(Task); the
    # subagent-creation surface is SubagentStart, which supports additionalContext.
    try:
        codex_json = json.loads(codex_hooks)
    except json.JSONDecodeError as exc:
        fail(cid, f"codex.hooks.json is not valid JSON: {exc}")
        codex_json = {}
    subagent_start = codex_json.get("hooks", {}).get("SubagentStart", [])
    codex_advisor_wired = any(
        "advisor-card.mjs" in json.dumps(group.get("hooks", []))
        for group in subagent_start
    )
    if not codex_advisor_wired:
        fail(cid, "codex.hooks.json must wire SubagentStart → advisor-card.mjs")
    codex_cfg = (ROOT / "agent-kit" / "hooks" / "clients" / "codex.config.toml").read_text(
        encoding="utf-8"
    )
    if "hooks" not in codex_cfg or "true" not in codex_cfg:
        fail(cid, "codex.config.toml must enable features.hooks")

    # If a local install already materialized client trees, they must match SSOT wiring.
    installed = [
        (ROOT / ".cursor" / "hooks.json", "cursor-hook.mjs"),
        (ROOT / ".cursor" / "hooks.json", "prompt-skill-router.mjs"),
        (ROOT / ".claude" / "settings.json", "hook-router.mjs"),
        (ROOT / ".claude" / "settings.json", "prompt-skill-router.mjs"),
        (ROOT / ".codex" / "hooks.json", "hook-router.mjs"),
        (ROOT / ".codex" / "hooks.json", "prompt-skill-router.mjs"),
    ]
    for path, marker in installed:
        if path.is_file() and marker not in path.read_text(encoding="utf-8"):
            fail(cid, f"installed {path.relative_to(ROOT)} missing {marker}")


def check_public_subject_gates() -> None:
    """Run protocol checker on public example subjects that have green fixtures."""
    cid = "subject-gates-fixture"
    if not CHECK_SUBJECT_GATES.is_file():
        fail(cid, "missing check_subject_gates.py")
        return
    # Only the min (green) fixture must pass in the public suite.
    # --fixture forces fixture_root even if a private checkout exists (B4).
    proc = run(
        [
            sys.executable,
            str(CHECK_SUBJECT_GATES),
            "--manifest",
            str(MANIFEST_EXAMPLE),
            "--fixture",
            "--subject",
            "demo-coding-harness-min",
        ]
    )
    if proc.returncode != 0:
        fail(cid, proc.stderr.strip() or proc.stdout.strip() or "exit non-zero")
        return
    ok(cid, "demo-coding-harness-min")

    # Red fixture must fail when invoked
    proc_red = run(
        [
            sys.executable,
            str(CHECK_SUBJECT_GATES),
            "--manifest",
            str(MANIFEST_EXAMPLE),
            "--fixture",
            "--subject",
            "demo-coding-harness-red",
        ]
    )
    if proc_red.returncode == 0:
        fail(cid, "demo-coding-harness-red should fail")
    else:
        ok(cid, "demo-coding-harness-red→red")


def check_no_private_suite_coupling() -> None:
    """Public suite source must not call private subject state checkers."""
    cid = "public-suite-decoupled"
    src = (ROOT / "tools" / "harness" / "checks.py").read_text(encoding="utf-8")
    banned_calls = (
        "check_pin_and_subs",
        "check_checkout_sample",
        "check_snapshot_schema",
    )
    for token in banned_calls:
        if re.search(rf"\b{re.escape(token)}\s*\(", src):
            fail(cid, f"public checks.py still calls {token}(")
            return
    # Must not bind a module-level private manifest constant for suite input.
    if re.search(
        r'^MANIFEST\s*=\s*ROOT\s*/\s*["\']subjects["\']\s*/\s*["\']manifest\.yaml["\']',
        src,
        re.M,
    ):
        fail(cid, "public checks.py must not bind MANIFEST to private subjects/manifest.yaml")
        return
    ok(cid, "no private pin/checkout/snapshot coupling")


def check_public_tree_desensitize() -> None:
    """Public-tree file bodies must not embed private absorb details."""
    cid = "public-tree-desensitize"
    from public_tree_desensitize import scan_public_tree  # noqa: WPS433

    findings = scan_public_tree(ROOT)
    if findings:
        sample = "; ".join(f"{rel}: {hit}" for rel, hit in findings[:8])
        more = f" (+{len(findings) - 8} more)" if len(findings) > 8 else ""
        fail(cid, f"{len(findings)} leak(s) — {sample}{more}")
        return
    ok(cid, "no private content in public tree")


def ensure_runtime_ledgers() -> None:
    ge = ROOT / "docs" / "harness" / "gate-events.jsonl"
    if not ge.exists():
        ge.parent.mkdir(parents=True, exist_ok=True)
        ge.write_text("", encoding="utf-8")
    reports = ROOT / "docs" / "harness" / "reports"
    reports.mkdir(parents=True, exist_ok=True)


def main() -> int:
    if not MANIFEST_EXAMPLE.is_file():
        print("FAIL  missing subjects/manifest.example.yaml", file=sys.stderr)
        return 1
    text = MANIFEST_EXAMPLE.read_text(encoding="utf-8")
    ensure_runtime_ledgers()
    print(f"== harness public trusted suite @ {ROOT}")
    print("   manifest source: example (public only)")

    check_no_private_suite_coupling()
    check_public_tree_desensitize()
    check_client_trees_ignored()
    check_manifest_schema(text)
    check_submodule_fixture()
    check_symlink_health()
    check_no_business_default(text)
    check_private_gitignore()
    check_ledger_registry()
    check_docs_placement()
    check_hook_wiring()
    check_public_subject_gates()

    print("")
    if FAILS:
        print(f"✘ {len(FAILS)} failure(s)", file=sys.stderr)
        for f in FAILS:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("✔ harness 公開可信集通過")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
