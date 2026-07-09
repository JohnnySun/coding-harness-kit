"""Unit tests for public-tree content desensitization scanner."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from public_tree_desensitize import (
    find_leaks_in_text,
    is_scannable_path,
    load_private_registry_tokens,
    scan_paths,
)

_HOME_USER = "/Users/" + "alice"
_SUBJECT = "acme" + "-widget"


class TestPatternDetection(unittest.TestCase):
    def test_home_absolute_path_is_leak(self) -> None:
        hits = find_leaks_in_text(f'skill_path: "{_HOME_USER}/Work/ai-infra/skills/x"')
        self.assertTrue(any("absolute home path" in h for h in hits))

    def test_linux_home_absolute_path_is_leak(self) -> None:
        hits = find_leaks_in_text("see " + "/home/" + "bob" + "/projects/foo")
        self.assertTrue(any("absolute home path" in h for h in hits))

    def test_example_github_remote_is_clean(self) -> None:
        hits = find_leaks_in_text("remote: https://github.com/example/harness-demo-min.git")
        self.assertEqual(hits, [])

    def test_relative_subjects_checkout_mention_without_home_is_clean(self) -> None:
        # Relative path discussion in design docs is OK; absolute home+checkout is not.
        hits = find_leaks_in_text("checkout lives under subjects/<id>/checkout/")
        self.assertEqual(hits, [])

    def test_absolute_checkout_path_is_leak(self) -> None:
        hits = find_leaks_in_text(
            f"open {_HOME_USER}/Work/Harness-dev/subjects/demo/checkout/AGENTS.md"
        )
        self.assertTrue(any("checkout" in h for h in hits))


class TestPrivateRegistryTokens(unittest.TestCase):
    def test_subject_id_and_remote_from_manifest(self) -> None:
        remote = "git@github.com:acme/widget.git"
        text = (
            "subjects:\n"
            f"  {_SUBJECT}:\n"
            f"    remote: {remote}\n"
            "    default_branch: main\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.yaml"
            path.write_text(text, encoding="utf-8")
            ids, remotes = load_private_registry_tokens(path)
        self.assertIn(_SUBJECT, ids)
        self.assertIn(remote, remotes)

    def test_subject_id_banned_in_public_text(self) -> None:
        hits = find_leaks_in_text(
            f"ported via {_SUBJECT} 2026-07-09",
            subject_ids={_SUBJECT},
            remotes=set(),
        )
        self.assertTrue(any("private subject id" in h for h in hits))

    def test_subject_id_inside_hyphenated_token_does_not_false_positive(self) -> None:
        hits = find_leaks_in_text(
            f"see {_SUBJECT}-workflow-guide skill",
            subject_ids={_SUBJECT},
            remotes=set(),
        )
        self.assertEqual(hits, [])

    def test_private_remote_banned_in_public_text(self) -> None:
        remote = "git@github.com:acme/widget.git"
        hits = find_leaks_in_text(
            f"clone {remote} then compare",
            subject_ids=set(),
            remotes={remote},
        )
        self.assertTrue(any("private subject remote" in h for h in hits))


class TestPathFilter(unittest.TestCase):
    def test_public_docs_and_tools_are_scannable(self) -> None:
        self.assertTrue(is_scannable_path("docs/specs/20260709-x/spec.md"))
        self.assertTrue(is_scannable_path("tools/harness/checks.py"))
        self.assertTrue(is_scannable_path("agent-kit/hooks/clients/cursor.hooks.json"))

    def test_private_trees_and_submodule_skipped(self) -> None:
        self.assertFalse(is_scannable_path("subjects/manifest.yaml"))
        self.assertFalse(is_scannable_path("subjects/acme/checkout/AGENTS.md"))
        self.assertFalse(is_scannable_path("snapshots/x.json"))
        self.assertFalse(is_scannable_path("comparisons/x.md"))
        self.assertFalse(
            is_scannable_path(
                "agent-kit/skills/skills/writing-human-readable-docs/evals/runs/x.json"
            )
        )
        self.assertTrue(is_scannable_path("subjects/manifest.example.yaml"))


class TestScanPaths(unittest.TestCase):
    def test_scan_finds_leak_in_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rel = "docs/specs/demo/spec.md"
            path = root / rel
            path.parent.mkdir(parents=True)
            path.write_text(
                f"// via {_SUBJECT} 2026-07-09\nsee {_HOME_USER}/Work/x\n",
                encoding="utf-8",
            )
            findings = scan_paths(
                root,
                [rel],
                subject_ids={_SUBJECT},
                remotes=set(),
            )
        kinds = {hit for _, hit in findings}
        self.assertTrue(any("private subject id" in k for k in kinds))
        self.assertTrue(any("absolute home path" in k for k in kinds))

    def test_scan_passes_clean_public_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rel = "docs/specs/demo/spec.md"
            path = root / rel
            path.parent.mkdir(parents=True)
            path.write_text("public trusted suite only\n", encoding="utf-8")
            findings = scan_paths(root, [rel])
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
