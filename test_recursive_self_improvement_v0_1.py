from recursive_self_improvement_v0_1 import (
    ImprovementObservation,
    ImprovementProposal,
    ProposalEvaluation,
    RecursiveImprovementEngine,
)
import pytest


def observation():
    return ImprovementObservation(
        task_id="fixture-1",
        baseline={"accuracy": 0.5},
        evidence=("fixture-baseline",),
        uncertainty=0.2,
        observed_failures=("missed-contrast",),
    )


def proposal(obs, iteration, parent):
    return ImprovementProposal(
        proposal_id=f"p-{iteration}",
        parent_id=parent,
        change="add an explicit competing interpretation check",
        expected_gain=0.1,
        risks=("extra latency",),
        next_observation="replay the contrast fixture",
    )


def evaluate(obs, prop):
    return ProposalEvaluation(
        proposal_id=prop.proposal_id,
        metrics={"accuracy": obs.baseline["accuracy"] + 0.1},
        regressions=(),
        evidence=(f"replay:{prop.proposal_id}",),
        score=0.1,
    )


def test_shadow_run_is_bounded_and_chainable():
    receipts = RecursiveImprovementEngine(max_iterations=3).run_shadow(
        observation(), proposal, evaluate
    )
    assert len(receipts) == 3
    assert all(r.status == "SHADOW_PASS" for r in receipts)
    assert receipts[1].proposal.parent_id == "p-1"
    assert all(len(r.receipt_sha256) == 64 for r in receipts)


def test_forbidden_effect_fails_closed():
    def bad_evaluate(obs, prop):
        return ProposalEvaluation(
            proposal_id=prop.proposal_id,
            metrics=obs.baseline,
            regressions=("MODEL_WEIGHT_CHANGE",),
            evidence=(),
            score=0.2,
        )

    receipts = RecursiveImprovementEngine().run_shadow(observation(), proposal, bad_evaluate)
    assert len(receipts) == 1
    assert receipts[0].status == "HOLD_FORBIDDEN_EFFECT"


def test_apply_is_never_implicit():
    with pytest.raises(PermissionError):
        RecursiveImprovementEngine.apply()


def test_invalid_uncertainty_is_rejected():
    invalid = ImprovementObservation("x", {}, (), 1.1)
    with pytest.raises(ValueError):
        RecursiveImprovementEngine().run_shadow(invalid, proposal, evaluate)
