"""Offline shadow comparison harness for the recursive-improvement candidate.

Adapters are supplied by the caller and must be pure/local. The harness never
selects the candidate as the active route and treats timeout/cancellation as
test outcomes, not as permission to retry or escalate.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from threading import Event
from typing import Any, Callable, Mapping, Sequence


VERSION = "UNA_RECURSIVE_SELF_IMPROVEMENT_SHADOW_COMPARISON_V0_1"


@dataclass(frozen=True)
class ShadowCase:
    case_id: str
    input: Mapping[str, Any]
    expected: Mapping[str, Any]


@dataclass(frozen=True)
class RouteResult:
    status: str
    output: Mapping[str, Any]
    receipt_sha256: str


@dataclass(frozen=True)
class ShadowCaseResult:
    case_id: str
    baseline: RouteResult
    candidate: RouteResult
    outcome: str
    reason: str


@dataclass(frozen=True)
class ShadowReport:
    version: str
    route_under_test: str
    case_results: tuple[ShadowCaseResult, ...]
    candidate_selected: bool = False
    active_route_changed: bool = False
    report_sha256: str = ""

    def with_digest(self) -> "ShadowReport":
        payload = _plain(self)
        payload["report_sha256"] = ""
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return ShadowReport(**{**self.__dict__, "report_sha256": digest})


Route = Callable[[Mapping[str, Any], Event], Mapping[str, Any]]


def _plain(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {k: _plain(getattr(value, k)) for k in value.__dataclass_fields__}
    if isinstance(value, tuple):
        return [_plain(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    return value


def _receipt(output: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(output, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _run(route: Route, case: ShadowCase, timeout_s: float) -> RouteResult:
    cancel = Event()
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(route, case.input, cancel)
        try:
            output = future.result(timeout=timeout_s)
        except TimeoutError:
            cancel.set()
            return RouteResult("TIMEOUT", {}, "")
        except Exception as exc:  # adapter failures are evidence, never retries
            cancel.set()
            return RouteResult("ERROR", {"error_type": type(exc).__name__}, "")
        if cancel.is_set():
            return RouteResult("CANCELLED", {}, "")
        return RouteResult("OK", dict(output), _receipt(output))


def compare(
    cases: Sequence[ShadowCase],
    baseline: Route,
    candidate: Route,
    *,
    timeout_s: float = 1.0,
) -> ShadowReport:
    if not cases:
        raise ValueError("at least one fixture is required")
    if not 0 < timeout_s <= 10:
        raise ValueError("timeout_s must be between 0 and 10 seconds")
    results: list[ShadowCaseResult] = []
    for case in cases:
        old = _run(baseline, case, timeout_s)
        new = _run(candidate, case, timeout_s)
        if old.status != "OK" or new.status != "OK":
            outcome, reason = "HOLD_RUNTIME_FAILURE", "timeout, cancellation, or adapter error"
        elif new.output == case.expected and old.output != case.expected:
            outcome, reason = "CANDIDATE_IMPROVEMENT", "candidate matched expected fixture"
        elif new.output != case.expected:
            outcome, reason = "HOLD_CANDIDATE_MISS", "candidate did not match expected fixture"
        elif old.output == case.expected:
            outcome, reason = "NO_REGRESSION", "both routes matched expected fixture"
        else:
            outcome, reason = "HOLD_UNCLASSIFIED", "comparison requires review"
        results.append(ShadowCaseResult(case.case_id, old, new, outcome, reason))
    return ShadowReport(VERSION, "STAGED_DIAGNOSTIC", tuple(results)).with_digest()


def cancel_immediately(_input: Mapping[str, Any], cancel: Event) -> Mapping[str, Any]:
    cancel.set()
    return {"should_not": "be accepted"}


def sleep_forever(_input: Mapping[str, Any], cancel: Event) -> Mapping[str, Any]:
    # Cooperative fixture: proves timeout cancellation without leaving a live
    # worker behind. Real adapters must provide the same cancellation property.
    while not cancel.wait(0.01):
        pass
    return {}


__all__ = [
    "RouteResult",
    "ShadowCase",
    "ShadowCaseResult",
    "ShadowReport",
    "VERSION",
    "cancel_immediately",
    "compare",
    "sleep_forever",
]
