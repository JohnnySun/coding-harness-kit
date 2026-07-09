#!/usr/bin/env python3
"""Unit tests for subject-gate protocol checker (fixture-only, no private remotes)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools" / "harness" / "check_subject_gates.py"
EXAMPLE = ROOT / "subjects" / "manifest.example.yaml"


class TestSubjectGateProtocol(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_green_fixture(self) -> None:
        proc = self._run(
            "--manifest",
            str(EXAMPLE),
            "--fixture",
            "--subject",
            "demo-coding-harness-min",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_red_fixture(self) -> None:
        proc = self._run(
            "--manifest",
            str(EXAMPLE),
            "--fixture",
            "--subject",
            "demo-coding-harness-red",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("FAIL", proc.stderr)

    def test_checkout_preferred_over_fixture(self) -> None:
        """When checkout exists and --fixture is off, prefer checkout (B4)."""
        from unittest import mock

        sys.path.insert(0, str(ROOT / "tools" / "harness"))
        import check_subject_gates as mod  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            checkout = tmp_root / "subjects" / "demo" / "checkout"
            checkout.mkdir(parents=True)
            (checkout / "marker").write_text("checkout", encoding="utf-8")
            fixture = tmp_root / "testdata" / "demo"
            fixture.mkdir(parents=True)
            (fixture / "marker").write_text("fixture", encoding="utf-8")
            man = """schema_version: 1
subjects:
  demo:
    remote: https://example.com/x.git
    default_branch: main
    default_submodules: []
    harness_paths:
      - AGENTS.md
    trusted_suite: true
    fixture_root: testdata/demo
"""
            with mock.patch.object(mod, "ROOT", tmp_root):
                preferred = mod.resolve_subject_root(
                    "demo", man, None, force_fixture=False
                )
                self.assertEqual(preferred, checkout.resolve())
                forced = mod.resolve_subject_root(
                    "demo", man, None, force_fixture=True
                )
                self.assertEqual(forced, fixture.resolve())

    def test_root_escape_rejected(self) -> None:
        proc = self._run(
            "--manifest",
            str(EXAMPLE),
            "--subject",
            "demo-coding-harness-min",
            "--root",
            "/tmp",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("escapes", proc.stderr)

    def test_missing_suite_skips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            man = Path(tmp) / "m.yaml"
            man.write_text(
                """schema_version: 1
subjects:
  bare:
    remote: https://example.com/x.git
    default_branch: main
    default_submodules: []
    harness_paths:
      - AGENTS.md
""",
                encoding="utf-8",
            )
            proc = self._run("--manifest", str(man), "--subject", "bare")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("no trusted_suite", proc.stderr)

    def test_fixture_root_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            man = Path(tmp) / "m.yaml"
            man.write_text(
                """schema_version: 1
subjects:
  evil:
    remote: https://example.com/x.git
    default_branch: main
    default_submodules: []
    harness_paths:
      - AGENTS.md
    trusted_suite: true
    fixture_root: ../outside
""",
                encoding="utf-8",
            )
            proc = self._run("--manifest", str(man), "--subject", "evil")
            # SystemExit with message → exit code 1
            self.assertNotEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("escapes", proc.stderr)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
