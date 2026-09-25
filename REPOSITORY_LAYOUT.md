# Repository Layout — UNA Brain

This repository is the sanitized implementation and collaboration surface. The private runtime
environment remains separate.

## Public/sanitized repository

- Root Python modules: reusable bounded candidate implementations.
- `test_*.py`: model-free local verification.
- `*.md`: reusable design boundaries, candidate contracts, and sanitized receipts.
- `.github/workflows/`: repeatable test and private-material checks.

## Private runtime environment

The private runtime environment owns launch agents, credentials, connected services, source-specific
identifiers, Founder authorization packets, live receipts, runtime state, and deployment material.
Those artifacts must not be copied into this repository.

## Integration rule

Reusable implementation may move from the private runtime into this repository only after removing
machine-specific bindings and private operational state. Runtime integration proceeds in the other
direction only through a separately scoped, hash-bound change with its own receipt.

## Authority rule

GitHub is the sanitized collaboration and backup surface. The complete local Brain repository is
the current source of truth for the full artifact set. A future authority change requires an
explicit repository decision and a new receipt.
