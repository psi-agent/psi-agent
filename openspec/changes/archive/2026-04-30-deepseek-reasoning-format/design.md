## Context

DeepSeek's reasoning API uses a specific format:
- **Thinking toggle**: `{"thinking": {"type": "enabled/disabled"}}` - controls whether reasoning is on
- **Reasoning effort**: `{"reasoning_effort": "low/medium/high/max"}` - controls reasoning intensity

For Anthropic format, DeepSeek uses:
- **Thinking toggle**: Same as OpenAI format
- **Reasoning effort**: `{"output_config": {"effort": "low/medium/high/max"}}`

Current implementation issues:
1. Session only adds `reasoning_effort`, missing `thinking` toggle
2. Anthropic translator maps to `thinking.budget_tokens` (incorrect for DeepSeek)

## Goals / Non-Goals

**Goals:**
- Session adds both `thinking: {"type": "enabled"}` and `reasoning_effort` to all AI requests
- OpenAI completions passes through both parameters unchanged
- Anthropic translator maps `reasoning_effort` to `output_config.effort`
- Reasoning enabled by default, effort defaults to "medium"

**Non-Goals:**
- CLI flags to toggle reasoning on/off (can be added later)
- CLI flags to change reasoning effort level (can be added later)
- Support for `max` effort level (session won't use it by default)

## Decisions

### Decision 1: Always enable reasoning with `thinking: {"type": "enabled"}`

**Rationale:** User explicitly requested reasoning to be enabled by default. This ensures consistent extended thinking behavior.

**Alternatives considered:**
- Make it configurable - Adds complexity, user said "暂时不提供接口切换他们"
- Let provider decide - Inconsistent behavior across models

### Decision 2: Map `reasoning_effort` to `output_config.effort` for Anthropic

**Rationale:** This is DeepSeek's actual API format for Anthropic-style requests. The previous mapping to `thinking.budget_tokens` was incorrect.

**Alternatives considered:**
- Keep `thinking.budget_tokens` - Incorrect for DeepSeek API
- Pass through unchanged - DeepSeek expects `output_config.effort`

### Decision 3: Remove `REASONING_EFFORT_TO_BUDGET_TOKENS` constant

**Rationale:** No longer needed since we're using `output_config.effort` which accepts the same values as `reasoning_effort`.

## Risks / Trade-offs

**Risk: Other providers may not recognize `thinking` parameter**
→ Mitigation: Most APIs ignore unknown parameters. If issues arise, we can add provider-specific handling.

**Risk: Breaking change for existing Anthropic users**
→ Mitigation: The previous implementation was just added and not yet released. Impact is minimal.
