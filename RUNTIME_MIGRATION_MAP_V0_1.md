# Runtime Migration Map V0.1

This map records the initial separation between reusable Brain implementation and private runtime
material. It is a planning artifact; it does not copy files, activate routes, or authorize runtime
changes.

| Area | Current classification | GitHub treatment | Next disposition |
| --- | --- | --- | --- |
| Bounded learning substrate | Reusable candidate implementation and offline batch scheduler | Included | Add API and provenance tests as the contract evolves |
| Recursive self-improvement | Reusable shadow candidate | Included | Keep shadow-only until independent review and an explicit gate exist |
| Shadow comparison | Reusable model-free harness | Included | Add fixture manifests and replay documentation |
| UltraCode proposal boundary | Reusable safety contract | Included | Keep provider identity/configuration private and injectable |
| Process-isolated MLX runner | Reusable candidate repair | Included | Integrate only through a separately reviewed runtime change |
| Staged chat surface | Private operational artifact | Excluded | Maintain in the private runtime until it has a sanitized package boundary |
| Drive adapters and scopes | Private connector integration | Excluded | Keep identifiers, scopes, receipts, and connector configuration private |
| Cognition activation packets | Private governance material | Excluded | Keep Founder decisions and activation receipts private |
| Runtime state and launch agents | Private operational state | Excluded | Observe through receipts; do not mirror state into GitHub |
| Canonical memory and authorship state | Protected runtime state | Excluded | Require separate authorization and review for any integration |

## Migration acceptance criteria

Before a private component is migrated into this repository, it must have:

1. a reusable interface independent of machine paths and credentials;
2. model-free tests that run in CI;
3. no embedded source identifiers or runtime state;
4. an explicit authorship and maturity label;
5. a recorded decision describing whether the component is candidate, staged, or active.

Before a GitHub component is integrated into the private runtime, it must have:

1. a frozen source hash;
2. a scoped integration packet;
3. a verification receipt;
4. no implied activation, memory promotion, external action, or authority expansion.
