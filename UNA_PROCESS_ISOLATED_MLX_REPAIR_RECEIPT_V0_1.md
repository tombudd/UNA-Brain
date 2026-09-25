# Process-Isolated MLX Repair Receipt V0.1

**Authorship:** Codex, assisting/build-time co-developer; not UNA-1 or UNA-2.

Implemented and tested a candidate repair for the UltraCode local panel timeout flaw in:

`process_isolated_mlx_runner_v0_1.py`

The boundary:

- starts each local operation in a new process group;
- applies offline/no-proxy environment settings;
- enforces a hard process timeout;
- terminates the process group with TERM then KILL fallback;
- converts timeout, launch, exit, malformed-output, and non-object responses into typed
  `ABSTAINED` results;
- hash-binds the exact command and emits a receipt payload digest.

Verification:

```text
5 passed
```

This candidate has not replaced the implementation under the private runtime repository. Integrating it
there requires a separately authorized source change, then the unchanged frozen candidate must be
reviewed again. No route, memory, model, connector, or authority changed in this workspace.
