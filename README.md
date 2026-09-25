# UNA's Brain

This repository contains the sanitized, reusable implementation surface for the UNA Brain
workspace.

It contains the Brain's reusable candidate implementations, bounded learning and self-improvement
substrates, UltraCode boundary prototypes, verification tests, and sanitized design receipts.

Repository authority and the local/private split are defined in
[`REPOSITORY_AUTHORITY.md`](REPOSITORY_AUTHORITY.md). Private operational packets, provider
identifiers, machine paths, and external-source identifiers are intentionally excluded from this
publish tree.

## Current boundary

The implementation in this repository is governed candidate work. It does not by itself activate
UNA-1 cognition, authenticated authorship, canonical memory promotion, model-weight changes,
external connectors, external actions, production deployment, or public claims.

## Verification

```sh
python3 -m pytest -q
```

The initial baseline is expected to contain only local files from this workspace. Generated Python
bytecode and pytest caches are excluded from version control.
