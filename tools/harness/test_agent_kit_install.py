#!/usr/bin/env python3
"""L1 contract tests for agent-kit install (harness-dev).

Wired into tools/harness/test-harness.sh so the trusted suite cannot silently
drop install/validate/external/optional-plugin invariants.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENT_KIT = ROOT / "agent-kit"
INSTALL_PY = AGENT_KIT / "install" / "install.py"
PROFILE = "harness-dev"
CLIENTS = ("cursor", "cursor-cli", "claude", "codex", "codex-native")
OPTIONAL_PLUGINS = ("superpowers", "mattpocock-skills")
LOCAL_SKILLS = [
    "code-review",
    "handoff",
    "harness-builder",
    "harness-operate",
    "model-tier-prompting",
    "plan-review",
    "refine",
    "skill-creator",
    "workflow-design",
    "writing-human-readable-docs",
]


def _run_install(*args: str, output_root: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if output_root is not None:
        env["OUTPUT_ROOT"] = str(output_root)
    return subprocess.run(
        [
            "uv",
            "run",
            "--project",
            str(AGENT_KIT / "install"),
            "python",
            str(INSTALL_PY),
            *args,
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


class TestAgentKitInstallSurface(unittest.TestCase):
    """SSOT files + entrypoint must exist (gate against deleting the install surface)."""

    def test_ssot_files_present(self) -> None:
        required = [
            INSTALL_PY,
            AGENT_KIT / "manifest.json",
            AGENT_KIT / "external-skills.json",
            AGENT_KIT / "external-skills-lock.json",
            AGENT_KIT / "optional-plugins.json",
            AGENT_KIT / "optional-plugins-lock.json",
            AGENT_KIT / "install" / "constraints.json",
            AGENT_KIT / "install" / "pyproject.toml",
            AGENT_KIT / "hooks" / "hooks.json",
            AGENT_KIT / "hooks" / "clients" / "cursor.hooks.json",
            AGENT_KIT / "hooks" / "clients" / "claude.settings.json",
            AGENT_KIT / "hooks" / "clients" / "codex.hooks.json",
            AGENT_KIT / "hooks" / "clients" / "codex.config.toml",
            AGENT_KIT / "mcp" / "servers.json",
            ROOT / "tools" / "harness" / "agent-kit.sh",
        ]
        missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
        self.assertEqual(missing, [], f"missing agent-kit install SSOT: {missing}")

    def test_manifest_profile_lists_methodology_skills(self) -> None:
        manifest = json.loads((AGENT_KIT / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn(PROFILE, manifest["profiles"])
        skills = manifest["profiles"][PROFILE]["skills"]
        for name in LOCAL_SKILLS:
            self.assertIn(name, skills, f"profile missing local skill {name}")
        # F7: never promote subject business skills into harness-dev profile
        for banned in ("subject-workflow-guide", "pull-repo-bootstrap"):
            self.assertNotIn(banned, skills)

    def test_external_empty_optional_plugins_declared(self) -> None:
        external = json.loads((AGENT_KIT / "external-skills.json").read_text(encoding="utf-8"))
        optional = json.loads((AGENT_KIT / "optional-plugins.json").read_text(encoding="utf-8"))
        lock = json.loads((AGENT_KIT / "optional-plugins-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(external["profiles"].get(PROFILE, {}).get("skills", []), [])
        plugins = optional.get("plugins", {})
        for name in OPTIONAL_PLUGINS:
            self.assertIn(name, plugins)
            self.assertIn(name, lock.get("plugins", {}))
        matt = plugins["mattpocock-skills"]["skills"]
        for collision in ("code-review", "handoff"):
            self.assertNotIn(collision, matt)
        for name in OPTIONAL_PLUGINS:
            self.assertIn("cursor-cli", plugins[name]["clients"])
            self.assertIn("cursor", plugins[name]["clients"])
            self.assertIn("claude", plugins[name]["clients"])
            self.assertIn("codex", plugins[name]["clients"])


class TestAgentKitValidate(unittest.TestCase):
    def test_validate_harness_dev_clean(self) -> None:
        proc = _run_install("validate", "--profile", PROFILE)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        report = json.loads(proc.stdout)
        self.assertEqual(report["profile"], PROFILE)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["external_skills"], [])
        self.assertEqual(sorted(report["optional_plugins"]), sorted(OPTIONAL_PLUGINS))
        for name in LOCAL_SKILLS:
            self.assertIn(name, report["skills"])


class TestAgentKitDryRunInstall(unittest.TestCase):
    def test_each_client_dry_run_links_local_skills(self) -> None:
        skills_dirs = {
            "cursor": ".cursor/skills",
            "cursor-cli": ".cursor/skills",
            "claude": ".claude/skills",
            "codex": ".agents/skills",
            "codex-native": ".codex/skills",
        }
        for client, skills_dir in skills_dirs.items():
            with self.subTest(client=client), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                proc = _run_install(
                    "install",
                    "--client",
                    client,
                    "--profile",
                    PROFILE,
                    "--dry-run",
                    output_root=out,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
                plan = json.loads(proc.stdout)
                self.assertEqual(plan["client"], client)
                self.assertEqual(plan["optional_plugins"], [])
                self.assertEqual(plan["external_skills"], [])
                for name in LOCAL_SKILLS:
                    rel = f"{skills_dir}/{name}"
                    self.assertIn(rel, plan["targets"])
                    link = out / rel
                    self.assertTrue(link.is_symlink(), f"{rel} must be symlink")
                    expected = (AGENT_KIT / "skills" / "skills" / name).resolve()
                    self.assertEqual(
                        os.path.realpath(link),
                        os.path.realpath(expected),
                        f"{rel} → {os.path.realpath(link)} (expected {expected})",
                    )

    def test_optional_plugins_opt_in_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install",
                "--client",
                "cursor",
                "--profile",
                PROFILE,
                "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertEqual(json.loads(proc.stdout)["optional_plugins"], [])

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install",
                "--client",
                "cursor",
                "--profile",
                PROFILE,
                "--with-optional-plugin",
                "superpowers",
                "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            plan = json.loads(proc.stdout)
            self.assertEqual(plan["optional_plugins"], ["superpowers"])
            self.assertIn(".cursor/plugins/superpowers", plan["targets"])

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install",
                "--client",
                "cursor",
                "--profile",
                PROFILE,
                "--with-optional-plugin",
                "not-a-real-plugin",
                "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 2, proc.stdout)
            self.assertIn("unknown optional plugin", proc.stderr)

    def test_cursor_cli_opt_in_plugins_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install",
                "--client",
                "cursor-cli",
                "--profile",
                PROFILE,
                "--with-all-optional-plugins",
                "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            plan = json.loads(proc.stdout)
            self.assertEqual(sorted(plan["optional_plugins"]), sorted(OPTIONAL_PLUGINS))
            self.assertIn(".cursor/plugins/superpowers", plan["targets"])
            self.assertIn(".cursor/plugins/mattpocock-skills", plan["targets"])

    def test_install_writes_client_hook_surface(self) -> None:
        """Install materializes hooks/settings from agent-kit/hooks/clients/."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install",
                "--client",
                "cursor",
                "--profile",
                PROFILE,
                "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            plan = json.loads(proc.stdout)
            self.assertIn(".cursor/hooks.json", plan["targets"])
            hooks = json.loads((out / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
            self.assertIn("beforeShellExecution", hooks["hooks"])
            self.assertIn("beforeSubmitPrompt", hooks["hooks"])
            self.assertIn("cursor-hook.mjs", json.dumps(hooks))
            self.assertIn("prompt-skill-router.mjs", json.dumps(hooks))

    def test_install_writes_claude_prompt_skill_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install",
                "--client",
                "claude",
                "--profile",
                PROFILE,
                "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            settings = json.loads((out / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertIn("UserPromptSubmit", settings["hooks"])
            self.assertIn("prompt-skill-router.mjs", json.dumps(settings))

    def test_install_writes_claude_advisor_card_hook(self) -> None:
        """Claude install wires PreToolUse(Task) → advisor-card.mjs (dispatch tier card)."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install",
                "--client",
                "claude",
                "--profile",
                PROFILE,
                "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            settings = json.loads((out / ".claude" / "settings.json").read_text(encoding="utf-8"))
            pre_tool_use = settings["hooks"]["PreToolUse"]
            advisor_group = next(
                (
                    g
                    for g in pre_tool_use
                    if "Task" in str(g.get("matcher", ""))
                    and "advisor-card.mjs" in json.dumps(g.get("hooks", []))
                ),
                None,
            )
            self.assertIsNotNone(
                advisor_group,
                "claude install must wire PreToolUse(Task) → advisor-card.mjs",
            )

    def test_install_writes_claude_advisor_model(self) -> None:
        """Claude install materializes advisorModel (mechanism A: native advisor).

        Anthropic-API-only + experimental; the advisor only attaches when it is
        at least as capable as the main model, otherwise it silently no-ops.
        """
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install", "--client", "claude", "--profile", PROFILE, "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            settings = json.loads((out / ".claude" / "settings.json").read_text(encoding="utf-8"))
            advisor_model = settings.get("advisorModel")
            self.assertTrue(
                advisor_model in {"fable", "opus", "sonnet"}
                or str(advisor_model or "").startswith("claude-"),
                f"claude install must set advisorModel to a tier alias/model id; got {advisor_model!r}",
            )

    def test_cursor_does_not_wire_advisor_card(self) -> None:
        """Cursor has no dispatch/subagent-creation hook surface; must NOT wire it."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install", "--client", "cursor", "--profile", PROFILE, "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            hooks = (out / ".cursor" / "hooks.json").read_text(encoding="utf-8")
            self.assertNotIn("advisor-card.mjs", hooks)

    def test_install_writes_codex_advisor_card_hook(self) -> None:
        """Codex wires SubagentStart → advisor-card.mjs (mechanism B, degraded form).

        Codex has no PreToolUse(Task); its subagent-creation surface is
        SubagentStart, which supports hookSpecificOutput.additionalContext.
        """
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install", "--client", "codex", "--profile", PROFILE, "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            hooks = json.loads((out / ".codex" / "hooks.json").read_text(encoding="utf-8"))
            subagent_start = hooks["hooks"].get("SubagentStart", [])
            advisor_group = next(
                (
                    g
                    for g in subagent_start
                    if "advisor-card.mjs" in json.dumps(g.get("hooks", []))
                ),
                None,
            )
            self.assertIsNotNone(
                advisor_group,
                "codex install must wire SubagentStart → advisor-card.mjs",
            )

    def test_install_writes_codex_prompt_skill_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install",
                "--client",
                "codex",
                "--profile",
                PROFILE,
                "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            hooks = json.loads((out / ".codex" / "hooks.json").read_text(encoding="utf-8"))
            self.assertIn("UserPromptSubmit", hooks["hooks"])
            self.assertIn("prompt-skill-router.mjs", json.dumps(hooks))


class TestAgentKitCollisionGuards(unittest.TestCase):
    def test_install_resolved_skills_collision(self) -> None:
        sys.path.insert(0, str(AGENT_KIT / "install"))
        from install import install_resolved_skills  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_src = root / "_plugin" / "skills" / "code-review"
            skill_src.mkdir(parents=True)
            (skill_src / "SKILL.md").write_text("# x\n", encoding="utf-8")
            occupied = {"code-review"}
            with self.assertRaises(ValueError) as ctx:
                install_resolved_skills(
                    "test-plugin",
                    [("code-review", skill_src)],
                    root,
                    ".cursor/skills",
                    occupied,
                )
            self.assertIn("collides", str(ctx.exception))
            self.assertFalse((root / ".cursor" / "skills" / "code-review").exists())


class TestAgentKitWrapper(unittest.TestCase):
    def test_wrapper_validate(self) -> None:
        proc = subprocess.run(
            ["bash", str(ROOT / "tools" / "harness" / "agent-kit.sh"), "validate"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_wrapper_install_no_dry_run_flag(self) -> None:
        """set -u must not trip on empty DRY/PLUGIN arrays (real install path)."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = subprocess.run(
                ["bash", str(ROOT / "tools" / "harness" / "agent-kit.sh"), "install"],
                cwd=ROOT,
                env={**os.environ, "CLIENT": "cursor", "OUTPUT_ROOT": str(out)},
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue((out / ".cursor" / "skills" / "harness-builder").is_symlink())
            self.assertTrue((out / ".cursor" / "hooks.json").is_file())


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
