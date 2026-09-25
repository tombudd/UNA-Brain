"""Killable process boundary for local UltraCode/MLX operations.

This is a candidate repair artifact. It deliberately uses subprocesses rather
than threads so a stalled MLX load/generation can be terminated and converted
into a typed abstention. No provider output is applied or promoted here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
import signal
import subprocess
from typing import Any, Mapping, Sequence


VERSION = "UNA_PROCESS_ISOLATED_MLX_RUNNER_V0_1"


@dataclass(frozen=True)
class IsolatedMLXResult:
    status: str
    output: Mapping[str, Any]
    reason: str
    elapsed_ms: int
    command_sha256: str

    @property
    def abstained(self) -> bool:
        return self.status == "ABSTAINED"


def _command_digest(command: Sequence[str]) -> str:
    return hashlib.sha256(
        json.dumps(list(command), separators=(",", ":")).encode()
    ).hexdigest()


def _offline_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        env.pop(key, None)
    env.update({
        "NO_PROXY": "*",
        "no_proxy": "*",
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_DATASETS_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "DO_NOT_TRACK": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    return env


def _abstain(command: Sequence[str], reason: str, elapsed_ms: int = 0) -> IsolatedMLXResult:
    return IsolatedMLXResult("ABSTAINED", {}, reason, elapsed_ms, _command_digest(command))


def run_json(
    command: Sequence[str],
    request: Mapping[str, Any],
    *,
    timeout_s: float = 30.0,
) -> IsolatedMLXResult:
    """Execute one offline JSON operation in a killable process group."""
    if not command:
        raise ValueError("command is required")
    if not 0 < timeout_s <= 600:
        raise ValueError("timeout_s must be between 0 and 600 seconds")
    started = __import__("time").monotonic()
    proc: subprocess.Popen[str] | None = None
    try:
        proc = subprocess.Popen(
            list(command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=_offline_env(),
            start_new_session=True,
        )
        payload = json.dumps(dict(request), sort_keys=True, separators=(",", ":")) + "\n"
        stdout, stderr = proc.communicate(payload, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        if proc is not None and proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=1)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        elapsed = int((__import__("time").monotonic() - started) * 1000)
        return _abstain(command, f"hard process timeout after {timeout_s}s", elapsed)
    except OSError as exc:
        elapsed = int((__import__("time").monotonic() - started) * 1000)
        return _abstain(command, f"cannot start local executor: {type(exc).__name__}", elapsed)

    elapsed = int((__import__("time").monotonic() - started) * 1000)
    if proc.returncode != 0:
        detail = (stderr or stdout).strip().replace("\n", " ")[:240]
        return _abstain(command, f"child exit {proc.returncode}: {detail}", elapsed)
    try:
        decoded = json.loads(stdout)
    except json.JSONDecodeError:
        return _abstain(command, "child returned non-JSON output", elapsed)
    if not isinstance(decoded, dict):
        return _abstain(command, "child returned JSON that is not an object", elapsed)
    return IsolatedMLXResult("COMPLETED", decoded, "", elapsed, _command_digest(command))


def receipt_payload(result: IsolatedMLXResult) -> dict[str, Any]:
    payload = {"version": VERSION, **asdict(result)}
    payload["receipt_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


__all__ = ["IsolatedMLXResult", "VERSION", "receipt_payload", "run_json"]
