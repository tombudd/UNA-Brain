"""Run one bounded shadow binding probe against the local UltraCode wrapper."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
import os
from threading import Event
from typing import Any, Mapping

from shadow_comparison_v0_1 import ShadowCase, compare


ULTRACODE = Path(os.environ.get("UNA_ULTRACODE_WRAPPER", "ultracode"))


def local_ultracode_probe(_input: Mapping[str, Any], cancel: Event) -> Mapping[str, Any]:
    if cancel.is_set():
        return {"status": "CANCELLED"}
    proc = subprocess.run(
        [str(ULTRACODE), "probe", "--reviewer", "local"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    if proc.returncode != 0:
        return {"status": "ERROR", "returncode": proc.returncode}
    return json.loads(proc.stdout)


def staged_diagnostic_baseline(_input: Mapping[str, Any], _cancel: Event) -> Mapping[str, Any]:
    return {"provider": "staged_diagnostic", "status": "STAGED_DIAGNOSTIC"}


def main() -> int:
    # The expected object is populated from the same single local probe. This
    # is a binding/health check, not a claim of cognition improvement.
    expected = local_ultracode_probe({}, Event())
    report = compare(
        (ShadowCase("ultracode-local-probe-1", {"purpose": "bind"}, expected),),
        staged_diagnostic_baseline,
        local_ultracode_probe,
        timeout_s=5,
    )
    print(json.dumps({
        "binding": {
            "wrapper": str(ULTRACODE),
            "wrapper_sha256": "",
            "backend": os.environ.get("UNA_ULTRACODE_BACKEND", "local-mlx-backend"),
            "backend_sha256": "",
            "network": "DENIED_BY_WRAPPER",
            "third_party_reviewer": "DENIED_BY_WRAPPER",
        },
        "probe": expected,
        "shadow_report": json.loads(json.dumps(report, default=lambda x: x.__dict__)),
        "status": "BOUND_CONFIGURED_UNPROBED",
        "active_route_changed": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
