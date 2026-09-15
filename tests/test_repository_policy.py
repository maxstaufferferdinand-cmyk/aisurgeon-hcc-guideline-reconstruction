from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_SUFFIXES = {
    ".csv",
    ".docx",
    ".jsonl",
    ".log",
    ".pdf",
    ".xlsx",
    ".xml",
    ".zip",
}
SKIP_DIRS = {".git", ".venv", "__pycache__"}
FORBIDDEN_LOCAL_PATHS = [
    "/" + "/".join(["mnt", "c", "living_guideline_platform"]),
    "/" + "/".join(["home", "maxstauffer"]),
]
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
]


def repository_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file():
            files.append(path)
    return files


class RepositoryPolicyTests(unittest.TestCase):
    def test_no_prohibited_artifact_extensions(self) -> None:
        offenders = [
            str(path.relative_to(ROOT))
            for path in repository_files()
            if path.suffix.lower() in PROHIBITED_SUFFIXES
        ]
        self.assertEqual(offenders, [])

    def test_no_user_specific_absolute_paths(self) -> None:
        offenders = []
        for path in repository_files():
            if path.suffix.lower() not in {".py", ".md", ".toml", ".cff", ".example", ".json"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if any(forbidden in text for forbidden in FORBIDDEN_LOCAL_PATHS):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_no_obvious_secret_values(self) -> None:
        offenders = []
        for path in repository_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_runtime_template_is_valid_json(self) -> None:
        data = json.loads((ROOT / "config" / "runtime.example.json").read_text(encoding="utf-8"))
        self.assertEqual(data["search_start"], "2012-07-01")
        self.assertEqual(data["search_end"], "2025-02-28")


if __name__ == "__main__":
    unittest.main()
