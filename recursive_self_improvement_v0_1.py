"""Bounded recursive self-improvement candidate for UNA.

This module is intentionally a shadow evaluator, not an activation path.  It can
generate and compare improvement proposals, but it cannot mutate runtime code,
memory, model weights, connectors, or the active cognition route.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import hashlib
import json
from typing import Callable, Mapping, Sequence


VERSION = "UNA_RECURSIVE_SELF_IMPROVEMENT_CANDIDATE_V0_1"
FORBIDDEN_EFFECTS = frozenset(
    {
        "ROUTE_REPLACEMENT",
        "MEMORY_PROMOTION",
        "MODEL_WEIGHT_CHANGE",
        "CONNECTOR_ACCESS",
        "EXTERNAL_ACTION",
        "PUBLIC_CLAIM",
        "AUTHORITY_EXPANSION",
        "AUTOMATIC_FILE_MUTATION",
    }
)


@dataclass(frozen=True)
class ImprovementObservation:
    task_id: str
    baseline: Mapping[str, float]
    evidence: tuple[str, ...]
    uncertainty: float
    observed_failures: tuple[str, ...] = ()


@dataclass(frozen=True)
class ImprovementProposal:
    proposal_id: str
    parent_id: str | None
    change: str
    expected_gain: float
    risks: tuple[str, ...]
    next_observation: str
    action_boundary: str = "SHADOW_EVALUATION_ONLY"


@dataclass(frozen=True)
class ProposalEvaluation:
    proposal_id: str
    metrics: Mapping[str, float]
    regressions: tuple[str, ...]
    evidence: tuple[str, ...]
    score: float


@dataclass(frozen=True)
class ImprovementReceipt:
    version: str
    task_id: str
    iteration: int
    status: str
    observation: ImprovementObservation
    proposal: ImprovementProposal
    evaluation: ProposalEvaluation
    effects: tuple[str, ...] = ()
    receipt_sha256: str = field(default="")

    def with_digest(self) -> "ImprovementReceipt":
        payload = asdict(self)
        payload["receipt_sha256"] = ""
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return replace(self, receipt_sha256=digest)


ProposalFn = Callable[[ImprovementObservation, int, str | None], ImprovementProposal]
EvaluateFn = Callable[[ImprovementObservation, ImprovementProposal], ProposalEvaluation]


class RecursiveImprovementEngine:
    """Run a deterministic, bounded improvement search without applying changes."""

    def __init__(self, *, max_iterations: int = 3, min_gain: float = 0.0) -> None:
        if not 1 <= max_iterations <= 8:
            raise ValueError("max_iterations must be between 1 and 8")
        if min_gain < 0:
            raise ValueError("min_gain must be non-negative")
        self.max_iterations = max_iterations
        self.min_gain = min_gain

    def run_shadow(
        self,
        observation: ImprovementObservation,
        propose: ProposalFn,
        evaluate: EvaluateFn,
    ) -> tuple[ImprovementReceipt, ...]:
        if not 0 <= observation.uncertainty <= 1:
            raise ValueError("uncertainty must be between 0 and 1")
        receipts: list[ImprovementReceipt] = []
        parent_id: str | None = None
        current = observation

        for iteration in range(1, self.max_iterations + 1):
            proposal = propose(current, iteration, parent_id)
            evaluation = evaluate(current, proposal)
            forbidden = set(evaluation.regressions) & FORBIDDEN_EFFECTS
            status = "HOLD_FORBIDDEN_EFFECT" if forbidden else "SHADOW_PASS"
            if evaluation.score - proposal.expected_gain < self.min_gain:
                status = "HOLD_INSUFFICIENT_EVIDENCE"
            if evaluation.regressions and not forbidden:
                status = "HOLD_REGRESSION"

            receipt = ImprovementReceipt(
                version=VERSION,
                task_id=observation.task_id,
                iteration=iteration,
                status=status,
                observation=current,
                proposal=proposal,
                evaluation=evaluation,
            ).with_digest()
            receipts.append(receipt)
            if status != "SHADOW_PASS":
                break

            # The next cycle may learn from the prior proposal, but only as a
            # session-local observation. No durable memory or code is changed.
            parent_id = proposal.proposal_id
            current = ImprovementObservation(
                task_id=current.task_id,
                baseline=evaluation.metrics,
                evidence=current.evidence + evaluation.evidence,
                uncertainty=min(1.0, current.uncertainty + 0.02),
                observed_failures=evaluation.regressions,
            )
        return tuple(receipts)

    @staticmethod
    def apply(*_args: object, **_kwargs: object) -> None:
        raise PermissionError(
            "V0.1 is shadow-only; application requires a separately implemented and approved gate"
        )


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


__all__ = [
    "FORBIDDEN_EFFECTS",
    "ImprovementObservation",
    "ImprovementProposal",
    "ProposalEvaluation",
    "ImprovementReceipt",
    "RecursiveImprovementEngine",
    "VERSION",
    "canonical_json",
]
