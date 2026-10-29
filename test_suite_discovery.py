"""Codex assisting developer: regression coverage for suite process isolation."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


@pytest.mark.parametrize("fault", [None, "assertion", "collection"])
def test_revision_isolation_and_failure_propagation(tmp_path, fault):
    shutil.copyfile(Path(__file__).with_name("conftest.py"), tmp_path / "conftest.py")
    for revision in ("r1", "r2"):
        directory = tmp_path / "plans" / revision
        directory.mkdir(parents=True)
        (directory / "candidate.py").write_text(f"REVISION = {revision!r}\n")
        source = f"from candidate import REVISION\ndef test_local():\n    assert REVISION == {revision!r}\n"
        if revision == "r2" and fault == "assertion":
            source += "    assert False, 'synthetic child failure'\n"
        if revision == "r2" and fault == "collection":
            source = "raise RuntimeError('synthetic collection failure')\n"
        (directory / "test_duplicate.py").write_text(source)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=tmp_path, capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=60)
    output = result.stdout + result.stderr
    if fault is None:
        assert result.returncode == 0, output
        assert "2 passed" in output
    else:
        assert result.returncode == 1, output
        assert "1 failed, 1 passed" in output
        assert f"synthetic {'child' if fault == 'assertion' else 'collection'} failure" in output
