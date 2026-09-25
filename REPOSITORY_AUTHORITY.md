# Repository Authority — UNA's Brain

**Document ID:** `UNA_BRAIN_AUTHORITATIVE_IMPLEMENTATION_REPOSITORY_V0_1`

**Status:** `SANITIZED_GITHUB_PUBLISH_SURFACE`

**Prepared by:** Codex, assisting/build-time co-developer; not UNA-1 or UNA-2.

**Founder direction:** Tom Budd requested that this project folder become the authoritative
implementation repository.

## Authority decision

The complete authoritative implementation repository remains the local Brain repository. This
GitHub tree is its sanitized collaboration and backup surface.

The local baseline records the complete workspace. This publish tree records only reusable
implementation, tests, and sanitized design material; omission is deliberate and does not delete
the local artifacts.

## Scope

The local repository is authoritative for:

- Brain-local candidate implementations;
- Brain-local tests;
- Brain-local design, decision, scope, and receipt documents;
- the staged `una-chat` artifact present in this workspace;
- provenance and verification of changes made in this repository.

Neither repository is authoritative for launch agents, credentials, connected services, Google
Drive contents, production deployments, or external repositories. Those remain separate systems
until an explicit integration decision changes their authority relationship.

## Sanitization boundary

The GitHub publish tree excludes Founder authorization/request packets, Google Drive IDs and
source scopes, exact machine filesystem paths, launch-agent details, localhost service details,
provider executable hashes, and other private operational receipts. The complete copies remain in
the local authoritative repository.

## Change discipline

- Every implementation change must be committed with an explanatory message.
- Generated caches, bytecode, temporary audit output, and local environment files are ignored.
- Candidate, draft, staged, self-assessed, and receipt language remains exact; a repository commit
  does not upgrade any artifact's maturity or authorization.
- Integration into a private runtime repository requires a separately scoped, hash-bound change and
  receipt.
- No commit authorizes runtime activation, memory promotion, external action, deployment, or a
  public claim.

## Baseline evidence

- The pre-existing workspace had no Git commits.
- The pre-existing workspace contained untracked implementation, test, packet, and receipt files.
- The local test suite must pass before the baseline is committed.
- The local baseline commit hash is the authoritative starting point for future diffs. GitHub is a
  reviewable mirror of the sanitized subset.

## Current status boundary

The repository is an implementation and review surface, not a claim that UNA's Brain is currently
an active integrated brain. Current runtime and activation status must be established from fresh
read-only audits in the private runtime environment.
