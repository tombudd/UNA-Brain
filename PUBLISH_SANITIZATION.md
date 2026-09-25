# GitHub Publish Sanitization

This tree is the sanitized GitHub collaboration surface for the private UNA Brain repository.

Excluded from publication:

- Founder authorization and execution-request packets;
- Google Drive folder identifiers and source allowlists;
- exact local filesystem, launch-agent, and localhost service paths;
- provider executable locations and hashes;
- private runtime readiness and activation receipts;
- staged chat and other artifacts containing private operational state.

The complete artifacts remain in the local authoritative repository. This exclusion is deliberate;
it is not deletion or a claim that the omitted work is unimportant.

The published code is candidate work. A GitHub commit does not activate runtime behavior, promote
memory, authorize external actions, or establish independent review.
