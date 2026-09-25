# UltraCode Migration Note V0.1

The Brain repository contains the reusable safety boundary for UltraCode proposals and the
process-isolated local-operation candidate runner.

The private runtime contains larger authorization-aware build backends, Docker fixture execution,
model bindings, and provider-specific configuration. Those are not byte-equivalent to these
contracts and are intentionally not copied into the sanitized repository.

The reusable boundary remains:

- local provider output is proposal-only;
- network and third-party model influence are denied by policy;
- direct application and memory writes are denied;
- local operations run behind a killable process boundary;
- timeout, launch, exit, malformed-output, and non-object results abstain;
- receipts are hash-bound and non-authorizing.

This note records a migration boundary, not UltraCode activation, provider-quality evidence, or
runtime integration.
