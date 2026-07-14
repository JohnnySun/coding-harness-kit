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
CORE_SP_SKILLS = (
    "test-driven-development",
    "systematic-debugging",
    "verification-before-completion",
    "requesting-code-review",
    "receiving-code-review",
)
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

TDD_SCOPE_START = "<!-- tdd-scope-contract:start -->"
TDD_SCOPE_END = "<!-- tdd-scope-contract:end -->"
CANONICAL_TDD_SCOPE = """
**TDD 必做**：工作改變可維護、可重現的行為，包括 reusable code、parser、
validator、generator、installer、recovery、可重現的 regression fix、
harness/hook/policy enforcement（含 gate）、release artifact、stable contract，以及危險 write path。先寫能因
缺少該行為而失敗的測試（Red），再做最小實作（Green）。

**TDD 不要求**：探索、研究、唯讀 terminal 查證、設計、規劃、純文檔、證據整理、
compiler diagnostics、throwaway probe，以及行為不變的結構搬移。若過程開始改變
任何可維護行為或產物契約，亦即行為改變的 maintained artifact 必須重新分類並切回 TDD。

分類只決定是否需要 Red→Green；**驗證獨立於 TDD**。免 TDD 的工作仍須用與風險
相稱的檢查證明產物正確，不能把「免寫測試」解讀成「免驗證」。
"""


def _normalize_policy(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def _tdd_scope_contract_matches(text: str) -> bool:
    if text.count(TDD_SCOPE_START) != 1 or text.count(TDD_SCOPE_END) != 1:
        return False
    start = text.index(TDD_SCOPE_START) + len(TDD_SCOPE_START)
    end = text.index(TDD_SCOPE_END, start)
    return _normalize_policy(text[start:end]) == _normalize_policy(CANONICAL_TDD_SCOPE)


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
            AGENT_KIT / "profile" / "agent-profile.default.yaml",
            AGENT_KIT / "profile" / "agent-profile.template.yaml",
            AGENT_KIT / "profile" / "agent-profile.schema.json",
            AGENT_KIT / "profile" / "agent-profile.mjs",
            AGENT_KIT / "profile" / "agent-profile-router.mjs",
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
    def test_plan_reviewer_reclassifies_behavior_changing_docs_for_tdd(self) -> None:
        reviewer_prompt = (
            AGENT_KIT
            / "skills"
            / "skills"
            / "plan-review"
            / "references"
            / "reviewer-prompts.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "docs、skill 或 policy 若改變 maintained behavior 或 artifact contract，必須重新分類並要求 TDD",
            " ".join(reviewer_prompt.split()),
        )

    def test_builder_and_operate_require_profile_check_when_adopted(self) -> None:
        skills_root = AGENT_KIT / "skills" / "skills"
        for name in ("harness-builder", "harness-operate"):
            with self.subTest(skill=name):
                text = (skills_root / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("agent-kit.sh profile check", text)
                self.assertIn("已有語義等價", text)
                self.assertIn("不覆寫既有 hooks", text)

    def test_installed_harness_operate_preserves_conditional_tdd_scope(self) -> None:
        """Shared source and installed clients expose the same scoped TDD contract."""
        source = AGENT_KIT / "skills" / "skills" / "harness-operate" / "SKILL.md"
        source_text = source.read_text(encoding="utf-8")
        self.assertTrue(_tdd_scope_contract_matches(source_text), "source TDD scope differs from canonical policy")

        contradictory = source_text.replace(
            TDD_SCOPE_END,
            "純文檔永遠不需要 TDD，即使改變 maintained artifact contract。\n" + TDD_SCOPE_END,
        )
        self.assertFalse(
            _tdd_scope_contract_matches(contradictory),
            "contradictory additions inside the bounded policy must be rejected",
        )

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
            installed = out / ".agents" / "skills" / "harness-operate" / "SKILL.md"
            self.assertTrue(installed.is_file())
            self.assertEqual(installed.read_text(encoding="utf-8"), source_text)

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
                self.assertEqual(plan["profile"]["effective"]["process_scaffold"], "lean")
                self.assertEqual(
                    sorted(plan["libraries"]["superpowers"]),
                    sorted(CORE_SP_SKILLS),
                )
                self.assertIn("grilling", plan["libraries"]["mattpocock-skills"])
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

    def test_optimal_libraries_are_default_without_full_plugin_bootstrap(self) -> None:
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
            self.assertEqual(plan["optional_plugins"], [])
            for skill in CORE_SP_SKILLS:
                self.assertIn(f".cursor/skills/{skill}", plan["targets"])
            self.assertIn(".cursor/skills/grilling", plan["targets"])
            self.assertNotIn(".cursor/skills/using-superpowers", plan["targets"])
            self.assertNotIn(".cursor/skills/brainstorming", plan["targets"])
            self.assertFalse(
                any(target.startswith(".cursor/plugins/superpowers") for target in plan["targets"])
            )
            self.assertFalse(
                any(target.startswith(".cursor/plugins/mattpocock-skills") for target in plan["targets"])
            )

    def test_unowned_legacy_plugin_requires_manual_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            legacy = out / ".cursor" / "plugins" / "superpowers"
            legacy.mkdir(parents=True)
            (legacy / "plugin.json").write_text('{"name":"custom"}\n', encoding="utf-8")
            proc = _run_install(
                "install", "--client", "cursor", "--profile", PROFILE, "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 2, proc.stdout)
            self.assertIn("manual_cleanup_required", proc.stderr)
            self.assertTrue(legacy.is_dir())

    def test_owned_legacy_plugin_is_planned_for_safe_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            legacy = out / ".cursor" / "plugins" / "superpowers"
            legacy.mkdir(parents=True)
            (legacy / "plugin.json").write_text('{"name":"superpowers"}\n', encoding="utf-8")
            state = out / ".harness" / "agent-profile-state.json"
            state.parent.mkdir(parents=True)
            state.write_text(
                json.dumps({
                    "schema_version": 1,
                    "clients": {
                        "cursor": {
                            "managed_plugin_roots": [".cursor/plugins/superpowers"],
                        },
                    },
                }),
                encoding="utf-8",
            )
            proc = _run_install(
                "install", "--client", "cursor", "--profile", PROFILE, "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            plan = json.loads(proc.stdout)
            self.assertIn(
                ".cursor/plugins/superpowers",
                plan["removed_managed_plugins"],
            )
            self.assertTrue(legacy.is_dir(), "dry-run must not mutate legacy output")

    def test_generated_client_tree_can_migrate_known_legacy_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / ".gitignore").write_text(".cursor/\n", encoding="utf-8")
            legacy = out / ".cursor" / "plugins" / "superpowers"
            legacy.mkdir(parents=True)
            (legacy / "plugin.json").write_text('{"name":"superpowers"}\n', encoding="utf-8")
            bootstrap = out / ".cursor" / "skills" / "using-superpowers"
            bootstrap.mkdir(parents=True)
            (bootstrap / "SKILL.md").write_text("# legacy bootstrap\n", encoding="utf-8")
            proc = _run_install(
                "install", "--client", "cursor", "--profile", PROFILE, "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            plan = json.loads(proc.stdout)
            self.assertIn(".cursor/plugins/superpowers", plan["removed_managed_plugins"])
            self.assertIn(
                "using-superpowers",
                plan["removed_legacy_bootstrap_skills"],
            )
            self.assertTrue(legacy.is_dir(), "dry-run must not mutate legacy output")
            self.assertTrue(bootstrap.is_dir(), "dry-run must not mutate bootstrap skill")

    def test_default_library_refuses_to_overwrite_unmanaged_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            skill = out / ".cursor" / "skills" / "grilling"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# user content\n", encoding="utf-8")
            proc = _run_install(
                "install", "--client", "cursor", "--profile", PROFILE, "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 2, proc.stdout)
            self.assertIn("unmanaged skill", proc.stderr)
            self.assertEqual(
                (skill / "SKILL.md").read_text(encoding="utf-8"),
                "# user content\n",
            )

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

    def test_codex_does_not_wire_subagent_start_advisor_card(self) -> None:
        """Codex must NOT wire SubagentStart → advisor-card.mjs.

        SubagentStart delivers additionalContext to the CHILD subagent
        (post-decision) — useless for the orchestrator's dispatch decision. The
        Codex advisor card now rides UserPromptSubmit → prompt-skill-router.mjs.
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
            self.assertIsNone(
                advisor_group,
                "codex must NOT wire SubagentStart → advisor-card.mjs "
                "(child-facing; advisor rides UserPromptSubmit router)",
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

    def test_install_writes_codex_schema_supported_top_level_fields(self) -> None:
        """Generated Codex hooks must not contain unknown top-level fields."""
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
            self.assertEqual(set(hooks), {"description", "hooks"})


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

    def test_wrapper_profile_show_and_set_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            show = subprocess.run(
                [
                    "bash", str(ROOT / "tools" / "harness" / "agent-kit.sh"),
                    "profile", "show", "--root", str(root), "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(show.returncode, 0, show.stderr + show.stdout)
            self.assertEqual(json.loads(show.stdout)["effective"]["process_scaffold"], "lean")
            set_local = subprocess.run(
                [
                    "bash", str(ROOT / "tools" / "harness" / "agent-kit.sh"),
                    "profile", "set", "reply_style", "concise",
                    "--root", str(root), "--local",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(set_local.returncode, 0, set_local.stderr + set_local.stdout)
            self.assertIn(
                "reply_style: concise",
                (root / ".harness" / "agent-profile.local.yaml").read_text(encoding="utf-8"),
            )

    def test_install_process_scaffold_delegates_to_profile_writer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = _run_install(
                "install", "--client", "cursor", "--profile", PROFILE,
                "--process-scaffold", "guided", "--dry-run",
                output_root=out,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            report = json.loads(proc.stdout)
            self.assertEqual(report["profile"]["effective"]["process_scaffold"], "guided")
            self.assertIn(
                "process_scaffold: guided",
                (out / ".harness" / "agent-profile.yaml").read_text(encoding="utf-8"),
            )

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
