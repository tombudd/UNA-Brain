import pytest

from ultracode_local_provider_v0_1 import UltraCodePolicy, UltraCodeProposal, accept_proposal


def policy():
    return UltraCodePolicy("LOCAL_ULTRACODE_DEV", "a" * 64)


def proposal(**overrides):
    values = dict(
        request_id="req-1",
        provider_id="LOCAL_ULTRACODE_DEV",
        proposal={"change": "improve contrast scoring"},
        evidence=("local-replay-1",),
        uncertainty=0.3,
        provenance={
            "provider_id": "LOCAL_ULTRACODE_DEV",
            "executable_sha256": "a" * 64,
            "network": "DENIED",
            "third_party_models": "DENIED",
        },
    )
    values.update(overrides)
    return UltraCodeProposal(**values)


def test_local_provider_output_is_review_only():
    result = accept_proposal(policy(), proposal())
    assert result["status"] == "RECEIVED_FOR_SHADOW_REVIEW"
    assert result["memory_write"] is False
    assert result["route_change"] is False
    assert result["authority_change"] is False


def test_network_or_third_party_influence_fails_closed():
    with pytest.raises(PermissionError):
        accept_proposal(policy(), proposal(provenance={
            "provider_id": "LOCAL_ULTRACODE_DEV",
            "executable_sha256": "a" * 64,
            "network": "ALLOWED",
            "third_party_models": "DENIED",
        }))


def test_provider_mismatch_fails_closed():
    with pytest.raises(ValueError):
        accept_proposal(policy(), proposal(provider_id="LOCAL_ULTRACODE_OTHER"))


def test_policy_rejects_direct_apply():
    with pytest.raises(PermissionError):
        UltraCodePolicy("LOCAL_ULTRACODE_DEV", "a" * 64, direct_apply_allowed=True).validate()
