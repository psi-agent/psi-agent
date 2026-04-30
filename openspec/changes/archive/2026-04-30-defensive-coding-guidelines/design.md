## Context

psi-agent processes data from external sources (LLM providers, user input) that may have null or missing fields. The OpenAI streaming API specification explicitly allows fields to be `null` or absent in delta chunks. Different providers (OpenRouter, Tencent hy3, Anthropic) may have slightly different implementations.

The current codebase has inconsistent null-handling patterns:
- Some places use `dict.get("key", default)` with defaults
- Some places use `"key" in dict` checks
- Some places assume non-null without checks

## Goals / Non-Goals

**Goals:**
- Establish consistent defensive coding patterns for null-safety
- Add guidelines to CLAUDE.md for future development
- Fix all identified null-safety issues in streaming code paths

**Non-Goals:**
- Changing the streaming protocol or API
- Refactoring unrelated code
- Adding validation for all possible fields (focus on crash points)

## Decisions

**Decision 1: Standardize on `dict.get()` pattern for null checks**

Use `dict.get("key") is not None` for null checks before operations:

```python
# Preferred pattern
if data.get("field") is not None:
    result += data["field"]

# Also acceptable for optional defaults
value = data.get("field", "")
```

Rationale: `dict.get()` handles both missing keys and null values uniformly.

**Decision 2: Add defensive coding guidelines to CLAUDE.md**

Add a ~20 line section covering:
- Null-safety patterns for external data
- When to use defensive checks
- Common patterns to avoid

**Decision 3: Apply fixes systematically by component**

Order of fixes (by crash risk):
1. psi-session/runner.py - streaming delta processing (highest risk)
2. psi-ai/*/client.py - streaming response handling
3. psi-channel/*/client.py - streaming display
4. Other utility code

## Risks / Trade-offs

**Risk: Changes may introduce subtle behavior differences**
→ Mitigation: Use `is not None` checks that preserve empty string behavior

**Risk: Guidelines may not be followed in future code**
→ Mitigation: Add to CLAUDE.md so AI assistants and developers see it
