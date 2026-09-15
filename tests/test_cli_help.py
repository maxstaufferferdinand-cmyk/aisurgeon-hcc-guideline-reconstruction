from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATHS = sorted((ROOT / "src").glob("hcc_*.py"))


class CliHelpTests(unittest.TestCase):
    def test_all_runtime_scripts_have_help(self) -> None:
        for path in SCRIPT_PATHS:
            with self.subTest(path=path.relative_to(ROOT)):
                proc = subprocess.run(
                    [sys.executable, str(path), "--help"],
                    cwd=ROOT,
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=20,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("usage:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
