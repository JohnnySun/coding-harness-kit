"""Tests for optional-plugin skill discovery and collision detection.

Covers ``resolve_plugin_skills`` (nested-layout discovery via plugin.json's
``skills`` array, flat-scan fallback, and the fail-fast guards) and the
collision check inside ``install_optional_plugin`` (a plugin skill name
overlapping an already-occupied name must raise rather than silently clobber).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase, main as unittest_main

# Add install dir to path so `import install` resolves.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from install import (  # noqa: E402
    ensure_user_invoked_metadata,
    install_resolved_skills,
    remove_stale_managed_skills,
    resolve_plugin_skills,
    set_skill_description,
)


def _write_skill(root: Path, rel: str, body: str = "# skill\n") -> Path:
    """Create skills/<rel>/SKILL.md under root and return the skill dir."""
    skill_dir = root / rel
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body)
    return skill_dir


def _make_skill(skill_dir: Path, body: str = "# skill\n") -> Path:
    """Create <skill_dir>/SKILL.md (skill_dir is the full path) and return it."""
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body)
    return skill_dir


def _write_manifest(root: Path, skills: list[str] | None) -> None:
    """Write a plugin.json (post-copy2 state) with the given skills array.

    resolve_plugin_skills reads plugin_root/plugin.json — that is the manifest
    AFTER install_optional_plugin copies .claude-plugin/plugin.json to the
    plugin root (install.py:707). Tests stage the post-copy state directly.
    """
    manifest = {"name": "test-plugin"}
    if skills is not None:
        manifest["skills"] = skills
    (root / "plugin.json").write_text(json.dumps(manifest))


class TestResolvePluginSkills(TestCase):
    """resolve_plugin_skills: plugin.json-authoritative discovery + fail-fast guards."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.plugin_root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _plugin(self, skills_cfg) -> dict:
        return {"name": "test-plugin", "skills": skills_cfg}

    def test_declared_nested_skills_flattened(self) -> None:
        """plugin.json skills array → skills flat-copied by basename."""
        _write_manifest(
            self.plugin_root,
            ["./skills/engineering/tdd", "./skills/productivity/teach"],
        )
        _write_skill(self.plugin_root, "skills/engineering/tdd")
        _write_skill(self.plugin_root, "skills/productivity/teach")
        pairs = resolve_plugin_skills(self._plugin("*"), self.plugin_root)
        names = sorted(name for name, _ in pairs)
        self.assertEqual(names, ["tdd", "teach"])
        for _, src in pairs:
            self.assertTrue((src / "SKILL.md").exists())

    def test_undeclared_dirs_not_copied(self) -> None:
        """Undeclared nested dirs (e.g. deprecated/) are not resolved."""
        _write_manifest(self.plugin_root, ["./skills/engineering/tdd"])
        _write_skill(self.plugin_root, "skills/engineering/tdd")
        _write_skill(self.plugin_root, "skills/deprecated/legacy")  # not declared
        pairs = resolve_plugin_skills(self._plugin("*"), self.plugin_root)
        self.assertEqual([name for name, _ in pairs], ["tdd"])

    def test_fallback_flat_scan_when_no_skills_array(self) -> None:
        """No plugin.json skills array + '*' → flat skills/ scan (superpowers path)."""
        _write_manifest(self.plugin_root, None)  # manifest present, no skills key
        _write_skill(self.plugin_root, "skills/brainstorming")
        _write_skill(self.plugin_root, "skills/tdd")
        pairs = resolve_plugin_skills(self._plugin("*"), self.plugin_root)
        names = sorted(name for name, _ in pairs)
        self.assertEqual(names, ["brainstorming", "tdd"])

    def test_missing_declared_skill_raises(self) -> None:
        """A declared skill missing SKILL.md on disk raises (no silent skip)."""
        _write_manifest(self.plugin_root, ["./skills/engineering/tdd"])
        # NOTE: no skills/ tree created → declared skill is missing
        with self.assertRaises(ValueError) as ctx:
            resolve_plugin_skills(self._plugin("*"), self.plugin_root)
        self.assertIn("missing skill", str(ctx.exception))

    def test_duplicate_flattened_basename_raises(self) -> None:
        """Two declared skills flattening to the same basename raise."""
        _write_manifest(
            self.plugin_root,
            ["./skills/a/code", "./skills/b/code"],
        )
        _write_skill(self.plugin_root, "skills/a/code")
        _write_skill(self.plugin_root, "skills/b/code")
        with self.assertRaises(ValueError) as ctx:
            resolve_plugin_skills(self._plugin("*"), self.plugin_root)
        self.assertIn("duplicate flattened skill name", str(ctx.exception))

    def test_explicit_list_resolves_via_plugin_json(self) -> None:
        """Explicit skills list resolves each name via the plugin.json declaration."""
        _write_manifest(
            self.plugin_root,
            ["./skills/engineering/tdd", "./skills/engineering/code-review"],
        )
        _write_skill(self.plugin_root, "skills/engineering/tdd")
        _write_skill(self.plugin_root, "skills/engineering/code-review")
        pairs = resolve_plugin_skills(self._plugin(["tdd"]), self.plugin_root)
        self.assertEqual([name for name, _ in pairs], ["tdd"])
        # src path is the nested declared path, not skills/tdd
        _, src = pairs[0]
        self.assertEqual(src.name, "tdd")
        self.assertIn("engineering", src.as_posix())

    def test_explicit_list_name_not_in_manifest_raises(self) -> None:
        """An explicit list entry absent from plugin.json raises."""
        _write_manifest(self.plugin_root, ["./skills/engineering/tdd"])
        _write_skill(self.plugin_root, "skills/engineering/tdd")
        with self.assertRaises(ValueError) as ctx:
            resolve_plugin_skills(self._plugin(["nonexistent"]), self.plugin_root)
        self.assertIn("not declared in plugin.json", str(ctx.exception))

    def test_corrupt_plugin_json_raises(self) -> None:
        """A corrupt plugin.json raises rather than silently falling back."""
        (self.plugin_root / "plugin.json").write_text("{ not valid json")
        _write_skill(self.plugin_root, "skills/tdd")
        with self.assertRaises(ValueError) as ctx:
            resolve_plugin_skills(self._plugin("*"), self.plugin_root)
        self.assertIn("corrupt plugin.json", str(ctx.exception))

    def test_empty_declaration_raises(self) -> None:
        """An empty plugin.json skills array raises (no silent zero-skill install)."""
        _write_manifest(self.plugin_root, [])
        _write_skill(self.plugin_root, "skills/tdd")  # present but undeclared
        with self.assertRaises(ValueError) as ctx:
            resolve_plugin_skills(self._plugin("*"), self.plugin_root)
        self.assertIn("no skills resolved", str(ctx.exception))

    def test_explicit_list_without_manifest_uses_declared_skill_root(self) -> None:
        """An explicit skill_root resolves allowlisted skills without plugin hooks."""
        _write_skill(self.plugin_root, "skills/engineering/tdd")
        plugin = {
            "name": "test-plugin",
            "skills": ["tdd"],
            "skill_root": "skills",
        }
        pairs = resolve_plugin_skills(plugin, self.plugin_root)
        self.assertEqual([name for name, _ in pairs], ["tdd"])
        self.assertIn("engineering", pairs[0][1].as_posix())

    def test_path_escape_raises(self) -> None:
        """A declared path escaping plugin_root raises (defense-in-depth)."""
        # Declare a traversal path; normpath collapses it but is_relative_to rejects.
        _write_manifest(self.plugin_root, ["./skills/../../etc/passwd"])
        with self.assertRaises(ValueError) as ctx:
            resolve_plugin_skills(self._plugin("*"), self.plugin_root)
        self.assertIn("escapes plugin root", str(ctx.exception))


class TestInstallResolvedSkillsCollision(TestCase):
    """install_resolved_skills: collision with occupied_skill_names fails fast."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.output_root = Path(self.tmp.name)
        # A staged plugin skill source (mirrors a post-copy plugin_root skill dir).
        self.skill_src = self.output_root / "_plugin" / "skills" / "engineering" / "code-review"
        _make_skill(self.skill_src)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_collision_with_existing_skill_raises(self) -> None:
        """A plugin skill named like an occupied skill raises instead of clobbering."""
        resolved = [("code-review", self.skill_src)]
        occupied = {"code-review"}  # agent-kit's own code-review
        with self.assertRaises(ValueError) as ctx:
            install_resolved_skills(
                "test-plugin", resolved, self.output_root, ".claude/skills", occupied
            )
        self.assertIn("collides with an already-installed skill", str(ctx.exception))
        # The agent-kit skill dir must NOT have been created/overwritten.
        self.assertFalse((self.output_root / ".claude" / "skills" / "code-review").exists())
        # occupied set unchanged (the colliding name was not added).
        self.assertEqual(occupied, {"code-review"})

    def test_no_collision_installs_skill(self) -> None:
        """With no name collision, the plugin skill installs and is recorded as occupied."""
        resolved = [("code-review", self.skill_src)]
        occupied: set[str] = set()
        install_resolved_skills(
            "test-plugin", resolved, self.output_root, ".claude/skills", occupied
        )
        dst = self.output_root / ".claude" / "skills" / "code-review"
        self.assertTrue((dst / "SKILL.md").exists())
        self.assertIn("code-review", occupied)

    def test_collision_across_two_plugin_skills(self) -> None:
        """Two skills from the same plugin flattening to the same name: the second collides."""
        src_a = self.output_root / "_a" / "code"
        src_b = self.output_root / "_b" / "code"
        _make_skill(src_a)
        _make_skill(src_b)
        resolved = [("code", src_a), ("code", src_b)]
        with self.assertRaises(ValueError) as ctx:
            install_resolved_skills(
                "test-plugin", resolved, self.output_root, ".claude/skills", set()
            )
        self.assertIn("collides with an already-installed skill", str(ctx.exception))


class TestUserInvokedMetadata(TestCase):
    def test_matt_skill_frontmatter_is_marked_user_invoked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp)
            skill_md = skill / "SKILL.md"
            skill_md.write_text("---\nname: grilling\ndescription: Stress-test a plan.\n---\n\nBody.\n")
            ensure_user_invoked_metadata(skill)
            text = skill_md.read_text()
            self.assertIn("disable-model-invocation: true", text)
            self.assertEqual(text.count("disable-model-invocation:"), 1)

    def test_core_skill_description_can_encode_must_not_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp)
            skill_md = skill / "SKILL.md"
            skill_md.write_text(
                "---\nname: tdd\ndescription: Use for everything.\n---\n\nBody.\n"
            )
            set_skill_description(
                skill,
                "Use for maintained behavior; skip pure docs and research.",
            )
            text = skill_md.read_text()
            self.assertIn(
                "description: Use for maintained behavior; skip pure docs and research.",
                text,
            )
            self.assertNotIn("Use for everything", text)


class TestManagedStateCleanup(TestCase):
    def test_rejects_skill_name_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            victim = root / "victim"
            victim.mkdir()
            (victim / "keep").write_text("safe\n")
            with self.assertRaises(ValueError):
                remove_stale_managed_skills(
                    root,
                    ".cursor/skills",
                    ["../../../victim"],
                    set(),
                )
            self.assertTrue((victim / "keep").is_file())


if __name__ == "__main__":
    unittest_main()
