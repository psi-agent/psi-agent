## REMOVED Requirements

### Requirement: Session adds reasoning_effort to AI requests
**Reason**: Reasoning parameters should be handled at the AI layer, not session layer
**Migration**: Use `--thinking` and `--reasoning-effort` CLI flags when starting psi-ai-* components

## ADDED Requirements

### Requirement: OpenAI completions server injects reasoning parameters

The `OpenAICompletionsServer` SHALL inject `thinking` and `reasoning_effort` parameters into upstream API requests when configured via CLI.

#### Scenario: Thinking enabled via CLI
- **WHEN** psi-ai-openai-completions is started with `--thinking enabled`
- **THEN** all upstream requests SHALL include `thinking: {"type": "enabled"}`

#### Scenario: Reasoning effort set via CLI
- **WHEN** psi-ai-openai-completions is started with `--reasoning-effort medium`
- **THEN** all upstream requests SHALL include `reasoning_effort: "medium"`

#### Scenario: No reasoning parameters by default
- **WHEN** psi-ai-openai-completions is started without reasoning CLI flags
- **THEN** upstream requests SHALL NOT include `thinking` or `reasoning_effort` parameters

### Requirement: Anthropic messages server injects reasoning parameters

The `AnthropicMessagesServer` SHALL inject reasoning parameters into upstream API requests when configured via CLI, translating to Anthropic format.

#### Scenario: Thinking enabled via CLI
- **WHEN** psi-ai-anthropic-messages is started with `--thinking enabled`
- **THEN** all upstream requests SHALL include `thinking: {"type": "enabled"}`

#### Scenario: Reasoning effort set via CLI
- **WHEN** psi-ai-anthropic-messages is started with `--reasoning-effort medium`
- **THEN** all upstream requests SHALL include `output_config: {"effort": "medium"}`

#### Scenario: No reasoning parameters by default
- **WHEN** psi-ai-anthropic-messages is started without reasoning CLI flags
- **THEN** upstream requests SHALL NOT include reasoning-related parameters