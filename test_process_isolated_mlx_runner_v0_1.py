import json
import sys

from process_isolated_mlx_runner_v0_1 import receipt_payload, run_json


def child(code):
    return [sys.executable, "-c", code]


def test_successful_json_response_is_completed():
    result = run_json(child("import json; print(json.dumps({'ok': True}))"), {"x": 1})
    assert result.status == "COMPLETED"
    assert result.output == {"ok": True}
    assert len(receipt_payload(result)["receipt_sha256"]) == 64


def test_timeout_kills_child_and_abstains():
    result = run_json(child("import time; time.sleep(60)"), {}, timeout_s=0.05)
    assert result.status == "ABSTAINED"
    assert "hard process timeout" in result.reason
    assert result.elapsed_ms < 2000


def test_malformed_output_abstains():
    result = run_json(child("print('not json')"), {})
    assert result.status == "ABSTAINED"
    assert result.reason == "child returned non-JSON output"


def test_nonzero_exit_abstains():
    result = run_json(child("import sys; print('bad'); sys.exit(7)"), {})
    assert result.status == "ABSTAINED"
    assert "child exit 7" in result.reason


def test_offline_request_is_serialized_and_hash_bound():
    result = run_json(child("import sys, json; print(json.dumps(json.loads(sys.stdin.read())))"), {"a": 2})
    assert result.status == "COMPLETED"
    assert len(result.command_sha256) == 64
