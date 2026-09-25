"""Bounded autonomous-learning substrate for UNA.

This lane learns from explicitly supplied local sources by recording
provenance-bound candidate knowledge. It never trains weights, promotes
canonical memory, edits code, calls Ollama, or performs network I/O.

The local Apple Foundation Models/MLX interpreter may render a candidate for
the user, but the candidate content is created from the observed source by
this deterministic lane. That keeps the current interpreter boundary intact.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA = "UNA_CANDIDATE_LEARNING_RECORD_V0_1"
MAX_SOURCE_BYTES = 1_000_000
MAX_EXCERPTS = 8


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class LearningRecord:
    subject: str
    source_path: str
    source_sha256: str
    excerpts: tuple[str, ...]
    provider: str = "UNA_PRIMARY_COGNITION"
    status: str = "CANDIDATE_UNVERIFIED"

    def as_dict(self) -> dict:
        payload = {
            "schema": SCHEMA,
            "recorded_at": _now(),
            "subject": self.subject,
            "source": {"path": self.source_path, "sha256": self.source_sha256},
            "excerpts": list(self.excerpts),
            "provider": self.provider,
            "status": self.status,
            "memory_class": "NONCANONICAL_CANDIDATE",
            "memory_promoted": False,
            "model_weights_changed": False,
            "network_access": False,
            "external_action": False,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        payload["record_sha256"] = _sha256(canonical.encode())
        return payload


def observe_source(path: Path, subject: str) -> LearningRecord:
    """Observe a bounded UTF-8 text source and extract subject-bearing lines."""
    raw = path.read_bytes()
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError("SOURCE_EXCEEDS_BOUNDED_READ")
    text = raw.decode("utf-8", errors="replace")
    terms = [term for term in re.findall(r"[\w'-]+", subject.casefold()) if len(term) > 2]
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    matches = [line for line in lines if not terms or any(term in line.casefold() for term in terms)]
    excerpts = tuple((matches or lines)[:MAX_EXCERPTS])
    return LearningRecord(subject=" ".join(subject.split()), source_path=str(path),
                          source_sha256=_sha256(raw), excerpts=excerpts)


class CandidateLearningStore:
    """Append-only candidate store, deliberately separate from canonical memory."""

    def __init__(self, root: Path):
        self.path = Path(root) / "state" / "learning" / "candidate_records.jsonl"

    def append(self, record: LearningRecord) -> dict:
        payload = record.as_dict()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return payload

    def recall(self, subject: str = "") -> list[dict]:
        if not self.path.is_file():
            return []
        wanted = subject.casefold().strip()
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not wanted or wanted in str(row.get("subject", "")).casefold():
                rows.append(row)
        return rows


def learn(root: Path, subject: str, sources: Iterable[Path]) -> list[dict]:
    """Observe sources and persist candidate records for later governed review."""
    if not subject.strip():
        raise ValueError("SUBJECT_REQUIRED")
    store = CandidateLearningStore(root)
    return [store.append(observe_source(Path(source), subject)) for source in sources]


__all__ = ["CandidateLearningStore", "LearningRecord", "learn", "observe_source", "SCHEMA"]
