import json

import pytest

from shadow_comparison_v0_1 import ShadowCase, cancel_immediately, compare, sleep_forever


CASES = (ShadowCase("contrast-1", {"prompt": "ambiguous"}, {"answer": "qualified"}),)


def baseline(_input, _cancel):
    return {"answer": "unqualified"}


def candidate(_input, _cancel):
    return {"answer": "qualified"}


def test_candidate_improvement_is_reported_without_selection():
    report = compare(CASES, baseline, candidate)
    assert report.case_results[0].outcome == "CANDIDATE_IMPROVEMENT"
    assert report.route_under_test == "STAGED_DIAGNOSTIC"
    assert report.candidate_selected is False
    assert report.active_route_changed is False
    assert len(report.report_sha256) == 64


def test_replay_is_deterministic_for_same_adapters():
    first = compare(CASES, baseline, candidate)
    second = compare(CASES, baseline, candidate)
    assert first.report_sha256 == second.report_sha256


def test_cancellation_is_a_hold():
    report = compare(CASES, baseline, cancel_immediately)
    assert report.case_results[0].outcome == "HOLD_RUNTIME_FAILURE"


def test_timeout_is_a_hold():
    report = compare(CASES, baseline, sleep_forever, timeout_s=0.01)
    assert report.case_results[0].outcome == "HOLD_RUNTIME_FAILURE"


def test_empty_and_unbounded_inputs_rejected():
    with pytest.raises(ValueError):
        compare((), baseline, candidate)
    with pytest.raises(ValueError):
        compare(CASES, baseline, candidate, timeout_s=11)
