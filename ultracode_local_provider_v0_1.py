"""Fail-closed local UltraCode provider boundary for UNA cognition.

UltraCode output is treated as an untrusted, local proposal. This contract does
not assume UltraCode's implementation, model composition, or authorship. It
prevents third-party/network influence and prevents provider output from
directly changing code, memory, routes, or authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping


VERSION = "UNA_ULTRACODE_LOCAL_PROVIDER_CONTRACT_V0_1"


@dataclass(frozen=True)
class UltraCodePolicy:
    provider_id: str
    executable_sha256: str
    network_allowed: bool = False
    third_party_models_allowed: bool = False
    direct_apply_allowed: bool = False
    memory_write_allowed: bool = False

    def validate(self) -> None:
        if not self.provider_id.startswith("LOCAL_ULTRACODE_"):
            raise ValueError("provider must be explicitly local UltraCode")
        if len(self.executable_sha256) != 64 or any(
            c not in "0123456789abcdef" for c in self.executable_sha256
        ):
            raise ValueError("executable_sha256 must be lowercase SHA-256")
        if self.network_allowed or self.third_party_models_allowed:
            raise PermissionError("third-party or network influence is disabled")
        if self.direct_apply_allowed or self.memory_write_allowed:
            raise PermissionError("provider cannot apply changes or write memory")


@dataclass(frozen=True)
class UltraCodeProposal:
    request_id: str
    provider_id: str
    proposal: Mapping[str, Any]
    evidence: tuple[str, ...]
    uncertainty: float
    provenance: Mapping[str, str]
    action_boundary: str = "PROPOSAL_ONLY"

    def validate(self, policy: UltraCodePolicy) -> None:
        policy.validate()
        if self.provider_id != policy.provider_id:
            raise ValueError("proposal provider does not match policy")
        if not 0 <= self.uncertainty <= 1:
            raise ValueError("uncertainty must be between 0 and 1")
        required = {"provider_id", "executable_sha256", "network", "third_party_models"}
        if not required.issubset(self.provenance):
            raise ValueError("proposal provenance is incomplete")
        if self.provenance["provider_id"] != policy.provider_id:
            raise ValueError("provenance provider mismatch")
        if self.provenance["executable_sha256"] != policy.executable_sha256:
            raise ValueError("provenance executable mismatch")
        if self.provenance["network"] != "DENIED" or self.provenance["third_party_models"] != "DENIED":
            raise PermissionError("proposal contains disallowed influence")
        if self.action_boundary != "PROPOSAL_ONLY":
            raise PermissionError("UltraCode output must remain proposal-only")


def request_digest(request: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(request, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def accept_proposal(policy: UltraCodePolicy, proposal: UltraCodeProposal) -> dict[str, Any]:
    """Return a reviewable envelope; never apply the provider's proposal."""
    proposal.validate(policy)
    return {
        "status": "RECEIVED_FOR_SHADOW_REVIEW",
        "provider": proposal.provider_id,
        "request_id": proposal.request_id,
        "proposal": dict(proposal.proposal),
        "evidence": list(proposal.evidence),
        "uncertainty": proposal.uncertainty,
        "action_boundary": "PROPOSAL_ONLY",
        "memory_write": False,
        "route_change": False,
        "authority_change": False,
    }


__all__ = ["UltraCodePolicy", "UltraCodeProposal", "VERSION", "accept_proposal", "request_digest"]
