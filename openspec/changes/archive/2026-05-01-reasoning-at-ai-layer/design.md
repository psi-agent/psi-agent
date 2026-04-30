## Context

Current implementation adds `thinking` and `reasoning_effort` parameters at the session layer. This causes issues for models that don't support these parameters (e.g., standard GPT models, local models).

The architecture should respect separation of concerns:
- **Session layer**: Handles conversation flow, tool execution, history management
- **AI layer**: Handles provider-specific API formatting and parameters

## Goals / Non-Goals

**Goals:**
- Move reasoning parameter handling to psi-ai-* layer
- Allow per-provider configuration of reasoning parameters
- Default to no reasoning parameters (maximum compatibility)
- Support optional reasoning via CLI flags when using compatible models

**Non-Goals:**
- Auto-detection of model capabilities
- Per-request reasoning configuration
- Dynamic reasoning parameter adjustment

## Decisions

### Decision 1: Remove reasoning from session entirely

**Rationale:** Session should not know about provider-specific parameters. It's the AI layer's responsibility to inject provider-specific features.

**Alternatives considered:**
- Keep session config but make it optional - Still couples session to provider features
- Pass through unknown parameters - Doesn't solve the problem of session knowing about reasoning

### Decision 2: Add CLI flags to psi-ai-* components

**Rationale:** CLI flags are the simplest way to configure reasoning at startup. Users explicitly opt-in when they know their model supports it.

**CLI flags:**
- `--thinking <type>` - Enable thinking mode (e.g., "enabled", "disabled")
- `--reasoning-effort <level>` - Set reasoning effort (e.g., "low", "medium", "high")

### Decision 3: Default to no reasoning parameters

**Rationale:** Maximum compatibility. Models that don't support these parameters will work out of the box. Users who want reasoning must explicitly enable it.

## Risks / Trade-offs

**Risk: Users must manually enable reasoning for compatible models**
→ Mitigation: Document which models support reasoning and how to enable it

**Risk: Breaking change for existing users expecting reasoning**
→ Mitigation: This is a new feature branch, not yet released. Impact is minimal.
