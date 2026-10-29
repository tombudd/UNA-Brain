"""Codex assisting developer, at Founder's direction: isolate revision suites."""
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parent
SKIP = {"__pycache__", "node_modules", "venv", "build", "dist"}


def suite_files(root):
    """Group nested tests by directory, without importing candidate modules."""
    for directory, children, files in os.walk(root):
        children[:] = sorted(n for n in children if not n.startswith(".") and n not in SKIP)
        tests = sorted(n for n in files if n.endswith(".py") and
                       (n.startswith("test_") or n.endswith("_test.py")))
        if tests:
            yield Path(directory), tests


class IsolatedSuite(pytest.Item):
    def __init__(self, *, files, **kwargs):
        super().__init__(**kwargs)
        self.files = files

    def runtest(self):
        command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                   "--confcutdir", str(self.path), *self.files]
        result = subprocess.run(command, cwd=self.path, capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if result.returncode:
            pytest.fail(f"Suite exited {result.returncode}\n{result.stdout}{result.stderr}",
                        pytrace=False)
        print(result.stdout, end="")


class RevisionSuites(pytest.Directory):
    def collect(self):
        for directory, files in suite_files(self.path):
            yield IsolatedSuite.from_parent(
                self, name=directory.relative_to(ROOT).as_posix(), path=directory, files=files)


def pytest_collect_directory(path, parent):
    # Root tests use normal pytest collection. Each nested suite gets its own
    # interpreter so both test names and bare candidate imports stay local.
    if path.parent == ROOT:
        return RevisionSuites.from_parent(parent, path=path)
