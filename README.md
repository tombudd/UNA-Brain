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

Install the test dependency with `python3 -m pip install pytest`. Python 3.11 or
newer is supported; CI runs Python 3.11–3.14.

The standard command runs the root tests and all nested suites present in the
checkout. The root `conftest.py` groups nested tests by directory and runs each
group in a separate Python process. This preserves revision-local imports and
allows frozen revisions to reuse test filenames without collection collisions.
Hidden directories, `__pycache__`, `node_modules`, `venv`, `build`, and `dist`
are excluded from nested discovery. Untracked candidate suites run locally when
present; CI can run only suites included in its checkout.

Pytest's final count includes one item per nested suite, rather than every child
test. Use `python3 -m pytest -q -s` to see each child suite's counts. To select
individual tests within a revision, change to its test directory and run
`python3 -m pytest --confcutdir=. -q -k <expression>` there. A child failure or
collection error fails the standard command and includes the child output.

Test discovery assistance: Codex, assisting developer, at Tom Budd's direction.

The initial baseline is expected to contain only local files from this workspace. Generated Python
bytecode and pytest caches are excluded from version control.
