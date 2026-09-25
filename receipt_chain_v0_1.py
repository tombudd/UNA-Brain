"""Candidate-only tamper-evident receipt-chain contract.

This module validates in-memory receipt lineage. It does not read or write a
receipt store, execute work, promote memory, or grant authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

SCHEMA = "UNA1_CANDIDATE_RECEIPT_CHAIN_V0_1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_BOUNDARIES = {
    "runtime_mutation", "memory_promotion", "external_write",
    "authority_expansion", "network_attempted",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def receipt_sha256(receipt: Mapping[str, Any]) -> str:
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    return hashlib.sha256(_canonical(unsigned)).hexdigest()


def _validate_boundaries(value: Any) -> None:
    if (
        not isinstance(value, dict)
        or set(value) != _BOUNDARIES
        or any(type(item) is not bool or item is not False for item in value.values())
    ):
        raise ValueError("RECEIPT_CHAIN_BOUNDARIES_INVALID")


def validate_receipt(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("RECEIPT_CHAIN_RECEIPT_OBJECT_REQUIRED")
    expected = {
        "schema", "sequence", "receipt_id", "previous_receipt_sha256",
        "payload", "boundaries", "receipt_sha256",
    }
    if set(value) != expected or value.get("schema") != SCHEMA:
        raise ValueError("RECEIPT_CHAIN_RECEIPT_FIELDS_INVALID")
    if type(value.get("sequence")) is not int or value["sequence"] < 0:
        raise ValueError("RECEIPT_CHAIN_SEQUENCE_INVALID")
    if not isinstance(value.get("receipt_id"), str) or not value["receipt_id"].strip():
        raise ValueError("RECEIPT_CHAIN_RECEIPT_ID_INVALID")
    previous = value.get("previous_receipt_sha256")
    if previous is not None and (not isinstance(previous, str) or _SHA256.fullmatch(previous) is None):
        raise ValueError("RECEIPT_CHAIN_PREVIOUS_HASH_INVALID")
    if not isinstance(value.get("payload"), dict):
        raise ValueError("RECEIPT_CHAIN_PAYLOAD_INVALID")
    _validate_boundaries(value.get("boundaries"))
    digest = value.get("receipt_sha256")
    if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
        raise ValueError("RECEIPT_CHAIN_HASH_INVALID")
    if digest != receipt_sha256(value):
        raise ValueError("RECEIPT_CHAIN_HASH_MISMATCH")
    return value


def build_receipt(
    *,
    sequence: int,
    receipt_id: str,
    payload: dict[str, Any],
    previous_receipt_sha256: str | None = None,
) -> dict[str, Any]:
    unsigned = {
        "schema": SCHEMA,
        "sequence": sequence,
        "receipt_id": receipt_id,
        "previous_receipt_sha256": previous_receipt_sha256,
        "payload": payload,
        "boundaries": {key: False for key in sorted(_BOUNDARIES)},
    }
    value = {**unsigned, "receipt_sha256": receipt_sha256(unsigned)}
    return validate_receipt(value)


def verify_chain(receipts: Any) -> dict[str, Any]:
    """Verify contiguous, hash-linked receipts without accepting partial chains."""
    if not isinstance(receipts, list) or not receipts:
        raise ValueError("RECEIPT_CHAIN_LIST_REQUIRED")
    seen_ids: set[str] = set()
    previous_hash: str | None = None
    for expected_sequence, receipt in enumerate(receipts):
        validate_receipt(receipt)
        if receipt["sequence"] != expected_sequence:
            raise ValueError("RECEIPT_CHAIN_SEQUENCE_GAP")
        if receipt["receipt_id"] in seen_ids:
            raise ValueError("RECEIPT_CHAIN_DUPLICATE_ID")
        seen_ids.add(receipt["receipt_id"])
        if receipt["previous_receipt_sha256"] != previous_hash:
            raise ValueError("RECEIPT_CHAIN_PREVIOUS_HASH_MISMATCH")
        previous_hash = receipt["receipt_sha256"]
    return {
        "schema": "UNA1_CANDIDATE_RECEIPT_CHAIN_VERIFICATION_V0_1",
        "status": "PASS_RECEIPT_CHAIN_VERIFIED",
        "count": len(receipts),
        "headReceiptSha256": previous_hash,
        "boundaries": {key: False for key in sorted(_BOUNDARIES)},
        "claimBoundary": "CHAIN_INTEGRITY_NOT_EXECUTION_AUTHORITY_OR_MEMORY_PROVENANCE",
    }
