## Purpose

Unified reasoning control across different LLM providers, ensuring consistent extended thinking behavior using DeepSeek's API format.

## Requirements

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

### Requirement: OpenAI completions client passes through reasoning_effort

The `OpenAICompletionsClient` SHALL pass through both `thinking` and `reasoning_effort` parameters to the upstream OpenAI-compatible API without modification.

#### Scenario: Thinking toggle forwarded to OpenAI API
- **WHEN** request body contains `thinking` parameter
- **THEN** the parameter SHALL be included in the upstream API request
- **AND** the value SHALL NOT be modified

#### Scenario: Reasoning effort forwarded to OpenAI API
- **WHEN** request body contains `reasoning_effort` parameter
- **THEN** the parameter SHALL be included in the upstream API request
- **AND** the value SHALL NOT be modified

### Requirement: Anthropic messages translator maps reasoning_effort

The `translate_openai_to_anthropic` function SHALL map `reasoning_effort` to DeepSeek's `output_config.effort` format.

#### Scenario: Reasoning effort mapped to output_config
- **WHEN** request contains `reasoning_effort` parameter
- **THEN** the Anthropic request SHALL contain `output_config: {"effort": <value>}`
- **AND** the effort value SHALL be the same as reasoning_effort value

#### Scenario: No reasoning effort parameter
- **WHEN** request does not contain `reasoning_effort` parameter
- **THEN** no `output_config` SHALL be added to Anthropic request

#### Scenario: Thinking toggle passed through
- **WHEN** request contains `thinking` parameter
- **THEN** the Anthropic request SHALL include the same `thinking` parameter
