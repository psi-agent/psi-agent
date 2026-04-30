## Context

Different LLM providers have inconsistent default behavior for reasoning/extended thinking:
- Some models (e.g., Claude with extended thinking) enable reasoning by default or require explicit opt-in
- Others may not support reasoning at all or have different parameter names
- This creates unpredictable agent behavior when switching between models

The current architecture:
- Session (`runner.py`) builds request body and sends to AI component
- AI components (`openai_completions`, `anthropic_messages`) forward requests to upstream APIs
- No reasoning parameter is currently passed in requests

## Goals / Non-Goals

**Goals:**
- Session uniformly adds `reasoning_effort` parameter to all AI requests
- AI components pass through reasoning-related parameters transparently
- Consistent extended thinking behavior across different LLM providers

**Non-Goals:**
- Model-specific reasoning configuration (e.g., different reasoning levels per model)
- Runtime detection of reasoning support (models that don't support it will ignore the parameter)
- Exposing reasoning configuration to end users via CLI (can be added later if needed)

## Decisions

### Decision 1: Use `reasoning_effort` as the standard parameter name

**Rationale:** OpenAI uses `reasoning_effort` for o1/o3 models. This is the most widely adopted naming convention.

**Alternatives considered:**
- `thinking_budget` - Anthropic-specific naming
- `extended_thinking` - Too verbose
- Provider-specific parameters - Would require mapping logic in session

### Decision 2: Session adds reasoning parameter, AI components pass through

**Rationale:** Separation of concerns. Session decides WHAT parameters to include, AI components handle HOW to format them for the upstream API.

**Alternatives considered:**
- AI components add reasoning parameter - Would require model-specific logic in AI layer
- Channel provides reasoning parameter - Would leak LLM details to channel layer

### Decision 3: Default reasoning_effort to "medium"

**Rationale:** Provides a reasonable default that balances quality and cost. Users can override if needed.

**Alternatives considered:**
- No default (let model decide) - Inconsistent behavior across models
- "high" as default - Higher cost, may not be needed for all use cases
- "low" as default - May not provide sufficient reasoning quality

### Decision 4: Anthropic translator maps `reasoning_effort` to `thinking.budget_tokens`

**Rationale:** Anthropic uses a different parameter structure for extended thinking. The translator already handles format conversion between OpenAI and Anthropic formats.

**Mapping:**
- `reasoning_effort: "low"` → `thinking: { "budget_tokens": 1024 }`
- `reasoning_effort: "medium"` → `thinking: { "budget_tokens": 4096 }`
- `reasoning_effort: "high"` → `thinking: { "budget_tokens": 16384 }`

## Risks / Trade-offs

**Risk: Models that don't support reasoning may reject the parameter**
→ Mitigation: Most APIs ignore unknown parameters. If an API rejects it, we can add provider-specific handling later.

**Risk: Different models interpret reasoning_effort differently**
→ Mitigation: This is acceptable - the goal is consistent enabling of reasoning, not identical behavior.

**Risk: Increased token usage and cost**
→ Mitigation: Default to "medium" which provides reasonable reasoning without excessive cost. Document this in configuration.
