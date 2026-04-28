## Context

psi-agent uses workspace-level `System` classes to manage conversation history compaction. When history exceeds token limits, older messages are summarized or truncated. Two critical issues arise:

1. **Orphaned tool results**: If a tool_use block is removed but its tool_result remains, Anthropic/OpenAI APIs reject the transcript with errors like "unexpected tool_use_id".

2. **Lost identifiers**: LLM summarization may simplify important identifiers (UUIDs → "[UUID]", file paths → "the file"), breaking subsequent operations that need exact values.

The current implementation in `examples/an-openclaw-like-workspace/systems/system.py` has sophisticated summarization but lacks these safety mechanisms.

## Goals / Non-Goals

**Goals:**
- Ensure compacted history is always valid for API submission
- Preserve critical identifiers during summarization
- Handle edge cases: duplicate tool results, missing tool results, errored turns
- Maintain backward compatibility with existing workspace implementations

**Non-Goals:**
- Modifying the core psi-agent session runner (changes are workspace-level only)
- Implementing configurable identifier preservation policies (use strict mode only)
- Adding plugin hooks for compaction events

## Decisions

### Decision 1: Tool Result Pairing Repair Algorithm

**Chosen approach**: Single-pass repair after compaction

The algorithm:
1. Iterate through messages, tracking tool calls from assistant messages
2. When encountering a tool_result, check if it matches a pending tool call
3. Drop orphaned tool results (no matching tool call)
4. Drop duplicate tool results (same tool_call_id seen twice)
5. Optionally synthesize missing tool results for tool calls without results

**Alternatives considered**:
- **Pre-compaction marking**: Mark tool_use/result pairs before truncation, then ensure they're dropped together. Rejected because it requires modifying the truncation logic significantly.
- **Two-pass approach**: First pass identifies orphans, second pass removes them. Rejected as single-pass is more efficient.

### Decision 2: Identifier Preservation Strategy

**Chosen approach**: Add explicit instructions to summarization prompts

Add to `_HISTORY_SUMMARY_PROMPT` and `_UPDATE_SUMMARIZATION_PROMPT`:
```
PRESERVE all opaque identifiers exactly as written (no shortening or reconstruction), including:
- UUIDs and unique identifiers
- File paths and directory names
- URLs and API endpoints
- Hostnames, IPs, and ports
- Error codes and hash values
- Database keys and record IDs
```

**Alternatives considered**:
- **Post-processing extraction**: Try to extract and preserve identifiers from original text. Rejected as complex and error-prone.
- **Configurable policies**: Support strict/custom/off modes. Rejected as over-engineering for current needs; can add later if needed.

### Decision 3: Integration Point

**Chosen approach**: Repair at the end of `compact_history()` before returning

Call `repair_tool_use_result_pairing()` on the final compacted history. This ensures:
- Repair works regardless of whether summarization or truncation occurred
- Single integration point minimizes code changes
- Clear separation of concerns

## Risks / Trade-offs

**Risk: Repair may drop useful context**
→ Mitigation: Log when tool results are dropped; users can adjust `keep_recent_tokens` to preserve more context

**Risk: Identifier preservation may not work perfectly**
→ Mitigation: LLMs generally follow explicit instructions well; if issues arise, can enhance prompts

**Risk: Performance overhead**
→ Mitigation: Single-pass O(n) algorithm; negligible for typical conversation sizes
