import pytest

from receipt_chain_v0_1 import build_receipt, receipt_sha256, verify_chain


def _chain():
    first = build_receipt(sequence=0, receipt_id="r0", payload={"status": "HOLD"})
    second = build_receipt(
        sequence=1,
        receipt_id="r1",
        payload={"status": "PASS"},
        previous_receipt_sha256=first["receipt_sha256"],
    )
    return [first, second]


def test_receipt_chain_is_hash_linked_and_non_effectful():
    result = verify_chain(_chain())
    assert result["status"] == "PASS_RECEIPT_CHAIN_VERIFIED"
    assert result["count"] == 2
    assert all(item is False for item in result["boundaries"].values())


def test_receipt_tampering_is_rejected():
    chain = _chain()
    chain[0]["payload"]["status"] = "FORGED"
    with pytest.raises(ValueError, match="RECEIPT_CHAIN_HASH_MISMATCH"):
        verify_chain(chain)


def test_receipt_chain_rejects_gap_and_wrong_parent():
    chain = _chain()
    chain[1]["sequence"] = 3
    chain[1]["receipt_sha256"] = receipt_sha256(chain[1])
    with pytest.raises(ValueError, match="RECEIPT_CHAIN_SEQUENCE_GAP"):
        verify_chain(chain)


def test_receipt_chain_rejects_effectful_boundary_even_if_rehashed():
    chain = _chain()
    chain[1]["boundaries"]["memory_promotion"] = True
    chain[1]["receipt_sha256"] = receipt_sha256(chain[1])
    with pytest.raises(ValueError, match="RECEIPT_CHAIN_BOUNDARIES_INVALID"):
        verify_chain(chain)


def test_receipt_chain_requires_genesis_parent_to_be_null():
    chain = _chain()
    chain[0]["previous_receipt_sha256"] = "a" * 64
    chain[0]["receipt_sha256"] = receipt_sha256(chain[0])
    with pytest.raises(ValueError, match="RECEIPT_CHAIN_PREVIOUS_HASH_MISMATCH"):
        verify_chain(chain)


@pytest.mark.parametrize("suffix", ["x", "\n"])
def test_receipt_hash_bindings_require_exactly_64_hex_characters(suffix):
    chain = _chain()
    chain[1]["previous_receipt_sha256"] = chain[0]["receipt_sha256"] + suffix
    with pytest.raises(ValueError, match="RECEIPT_CHAIN_PREVIOUS_HASH_INVALID"):
        verify_chain(chain)
