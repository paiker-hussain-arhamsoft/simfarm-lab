# Simulation Safety Invariants

The Strategic Brain is simulation-only. Its safety contract is defined by the
hardcoded constants in [`backend/safety.py`](safety.py):

- `SIMULATED = True`
- `REQUIRES_INTERNET = False`
- `REAL_PII = False`
- `REAL_EXECUTION = False`

These values are deliberately not stored in `.env` files, environment
variables, or secrets. Sourcing an invariant from the environment would create
a silent runtime kill-switch: a deployment could set `SIMULATED=false` without
a reviewed code edit. Hardcoded constants require a reviewed source change and
a visible diff before the guarantee can be weakened.

## Enforcement

There are two independent enforcement mechanisms.

### Startup assertion

The main Strategic Brain startup handler calls the assertion before starting
the ledger scheduler:

```python
# backend/main.py:101
safety.assert_safety_invariants()
```

The isolated Tier 4 simulator registers its own startup handler:

```python
# backend/simfarm_service/app.py:16
safety.assert_safety_invariants()
```

`assert_safety_invariants()` is also the check that verifies the hardcoded
constants themselves. A weakened constant therefore prevents either service
from booting.

### Tool-result enforcement

Every registered tool result passes through the central runtime guard in
`registry.call_tool`:

```python
# backend/tools/registry.py:80
return safety.enforce_result(tool_id, result)
```

This catches a tool that tries to return `simulated=False`, an
internet-requiring result, or a result asserting real PII or other real
activity, even if the tool implementation was changed independently.

## Violation behavior

Both checks raise `SafetyInvariantError`. A startup violation causes the
service process to refuse boot. A tool-result violation hard-fails that tool
call instead of allowing an unsafe result to continue through the pipeline.

## Adding simulated tools

New simulated tools must return `simulated: True` and
`requires_internet: False`, use synthetic fixtures only, and never process real
PII or voter records. Do not introduce an environment flag or secret to toggle
these values. Keep the safety constants hardcoded and route every result
through the registry guard.
