# UNA Recursive Self-Improvement Candidate V0.1

**Authorship:** Codex, assisting/build-time co-developer; not UNA-1 or UNA-2.

**Maturity:** `PROPOSED` / shadow implementation. This is not an active UNA cognition route.

## Purpose

Add a recursive improvement loop to the proof-carrying cognition direction without granting
the loop authority to rewrite itself or the system around it. Each iteration carries a task,
baseline, evidence, uncertainty, proposal, risk, evaluation, next observation, and receipt.
The next iteration can use the previous result as a session-local observation, creating recursion
without hidden durable learning.

## Invariants

- Maximum eight iterations; default three.
- No network, connector, shell, model-weight, memory-promotion, route-replacement, or external
  action effect.
- No automatic file mutation: `apply()` always raises `PermissionError`.
- Regressions and forbidden effects fail closed with a typed HOLD status.
- Receipts are canonicalized and SHA-256 bound.
- Passing a shadow comparison does not authorize activation or a capability claim.

## Verification

Run:

```sh
python3 -m pytest -q test_recursive_self_improvement_v0_1.py
```

The implementation remains a candidate until it is independently reviewed, integrated through
the correct UNA route, and bound to an exact Founder authorization for any protected consequence.
