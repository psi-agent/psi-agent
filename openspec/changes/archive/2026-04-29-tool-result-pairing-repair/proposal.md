## Why

When conversation history is compacted (truncated or summarized), two critical issues can occur:

1. **Orphaned tool results**: tool_use blocks may be removed while their corresponding tool_result messages remain. This causes API errors from Anthropic and other strict providers, which reject transcripts where tool results don't have matching tool calls.

2. **Lost identifiers**: LLM summarization may "simplify" important identifiers like UUIDs, file paths, API endpoints, and error codes. This loses critical context needed for subsequent operations.

These are critical reliability issues - compaction can break the session entirely or render it unable to continue work.

## What Changes

### Tool Use/Result Pairing Repair

- Add `repair_tool_use_result_pairing()` function to detect and remove orphaned tool results
- Add `extract_tool_calls_from_assistant()` helper to parse tool calls from assistant messages
- Add `extract_tool_result_id()` helper to extract tool call IDs from tool results
- Integrate repair into the compaction flow in `System.compact_history()`
- Handle edge cases: duplicate tool results, missing tool results, errored assistant turns

### Identifier Preservation in Summarization

- Add identifier preservation instructions to summarization prompts
- Default to "strict" mode: preserve all UUIDs, hashes, IDs, hostnames, IPs, ports, URLs, and file names exactly
- Support optional configuration for custom or off modes

## Capabilities

### New Capabilities

- `tool-result-pairing-repair`: Capability to detect and repair orphaned tool results after history compaction, ensuring tool_use/tool_result pairing integrity for API compatibility.

- `identifier-preservation`: Capability to preserve critical identifiers (UUIDs, paths, URLs, etc.) during LLM-based summarization, preventing loss of context needed for subsequent operations.

### Modified Capabilities

- None (these are new capabilities, not modifying existing spec behavior)

## Impact

- **Affected files**:
  - `examples/an-openclaw-like-workspace/systems/system.py` - Add repair functions, identifier preservation, and integrate into `compact_history()`
  - `examples/a-simple-bash-only-workspace/systems/system.py` - Add basic repair for consistency
- **API compatibility**: Ensures compacted history is always valid for Anthropic/OpenAI APIs
- **Context preservation**: Critical identifiers remain available after summarization
- **Dependencies**: None (pure Python implementation)
