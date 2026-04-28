## Context

Currently, all psi-agent CLI components accept sensitive credentials (API keys, tokens) via command line arguments. These are visible in:
- `ps aux` output
- `/proc/<pid>/cmdline`
- Process monitoring tools

This is a known security issue in multi-user environments. The `setproctitle` library provides a cross-platform solution to modify the process title at runtime, hiding the original command line arguments.

## Goals / Non-Goals

**Goals:**
- Hide sensitive CLI arguments from process listings after program starts
- Provide a reusable utility for all CLI entry points
- Document this as a security principle in CLAUDE.md

**Non-Goals:**
- Hide arguments during the brief window between process start and `setproctitle` call (this is a known limitation of the approach)
- Encrypt or otherwise protect the arguments in memory
- Replace CLI argument passing with environment variables or config files (those are separate concerns)

## Decisions

### 1. Use `setproctitle` library

**Rationale:** This is the de-facto standard Python library for process title manipulation. It's cross-platform (Linux, macOS, Windows, FreeBSD) and actively maintained.

**Alternatives considered:**
- `python-prctl`: Linux-only, more complex, overkill for this use case
- Manual `/proc/self/comm` manipulation: Platform-specific, fragile
- Environment variables: Doesn't solve the problem (visible in `/proc/<pid>/environ`)

### 2. Create utility module `psi_agent.utils.proctitle`

**Rationale:** Centralize the masking logic for:
- Consistent behavior across all CLI entry points
- Easy testing
- Single source of truth for sensitive parameter names

**Interface:**
```python
def mask_sensitive_args(sensitive_keys: list[str]) -> None:
    """Mask sensitive CLI arguments from process title.

    Args:
        sensitive_keys: List of argument names to mask (e.g., ['api_key', 'token'])
    """
```

### 3. Call masking immediately after CLI parsing

**Rationale:** Minimize the time window where arguments are visible. The `__call__` method in each CLI dataclass is the earliest point after tyro parsing where we have access to the parsed values.

## Risks / Trade-offs

- **Race condition**: There's a brief window (milliseconds) between process start and `setproctitle` call where arguments are visible. This is acceptable for our threat model.
- **Platform compatibility**: `setproctitle` works on most platforms but may have edge cases. We should handle ImportError gracefully.
- **Debugging**: Masked arguments may complicate debugging. Logs should still record that the program started (without the sensitive values).
