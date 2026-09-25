# UNA Recursive Improvement Shadow Comparison V0.1

**Authorship:** Codex, assisting/build-time co-developer; not UNA-1 or UNA-2.

This harness is an offline, fixture-driven comparison layer for the recursive-improvement
candidate. It compares an adapter representing `STAGED_DIAGNOSTIC` with a candidate adapter and
emits deterministic, hash-bound results. It does not select, activate, replace, or mutate either
route.

Required evidence before using real UNA fixtures:

- exact fixture manifest and hashes;
- exact baseline and candidate adapter identities;
- expected-output definitions and metric rubric;
- environment and dependency hashes;
- replay, cancellation, timeout, regression, and receipt-integrity results;
- separated review of the frozen candidate and rubric.

Current verification command:

```sh
python3 -m pytest -q test_recursive_self_improvement_v0_1.py test_shadow_comparison_v0_1.py
```

The included fixture is synthetic. It proves harness behavior, not UNA runtime improvement.
