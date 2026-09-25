"""Offline, allowlisted autonomous candidate-learning batch.

This is a batch learner, not a daemon. It discovers only bounded text files
placed in ``state/learning/inbox`` and records noncanonical candidates through
the existing learning substrate. It has no network, connector, promotion,
weight-training, or scheduler-install capability.
"""

from __future__ import annotations

from pathlib import Path

from una_autonomous_learning_v0_1 import MAX_SOURCE_BYTES, learn


INBOX = Path("state/learning/inbox")
ALLOWED_SUFFIXES = {".md", ".txt", ".json"}
MAX_FILES = 8


def discover(root: Path, limit: int = MAX_FILES) -> list[Path]:
    """Return bounded regular files from the fixed local learning inbox."""
    root = Path(root).resolve()
    inbox = (root / INBOX).resolve()
    if inbox != root / INBOX:
        raise ValueError("LEARNING_INBOX_PATH_INVALID")
    if not inbox.is_dir():
        return []
    files = []
    for path in sorted(inbox.iterdir()):
        if path.is_symlink() or not path.is_file() or path.suffix.casefold() not in ALLOWED_SUFFIXES:
            continue
        if path.stat().st_size > MAX_SOURCE_BYTES:
            continue
        files.append(path)
        if len(files) >= max(1, min(int(limit), MAX_FILES)):
            break
    return files


def run_once(root: Path, subject: str = "autonomous learning", limit: int = MAX_FILES) -> dict:
    """Discover inbox sources once and record candidate observations."""
    root = Path(root)
    sources = discover(root, limit=limit)
    if not sources:
        return {
            "schema": "UNA_LEARNING_AUTONOMOUS_BATCH_V0_1",
            "status": "PASS_NO_ALLOWLISTED_SOURCES",
            "discovered": [],
            "records": [],
            "memory_class": "NONCANONICAL_CANDIDATE",
            "memory_promoted": False,
            "network_access": False,
        }
    records = learn(root, subject, sources)
    return {
        "schema": "UNA_LEARNING_AUTONOMOUS_BATCH_V0_1",
        "status": "PASS_AUTONOMOUS_CANDIDATES_RECORDED",
        "discovered": [str(path.relative_to(root)) for path in sources],
        "records": records,
        "memory_class": "NONCANONICAL_CANDIDATE",
        "memory_promoted": False,
        "model_weights_changed": False,
        "network_access": False,
        "external_action": False,
        "scheduler_installed": False,
    }


__all__ = ["ALLOWED_SUFFIXES", "INBOX", "MAX_FILES", "discover", "run_once"]
