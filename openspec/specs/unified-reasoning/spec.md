## Purpose

Unified reasoning control across different LLM providers, ensuring consistent extended thinking behavior.

## Requirements

### Requirement: Session adds reasoning_effort to AI requests

The session SHALL include a `reasoning_effort` parameter in all requests sent to AI components.

#### Scenario: Reasoning effort included in request
- **WHEN** session sends a request to AI component
- **THEN** the request body SHALL contain `reasoning_effort` parameter
- **AND** the default value SHALL be "medium"

#### Scenario: Reasoning effort configurable
- **WHEN** session is configured with a specific reasoning_effort level
- **THEN** the request body SHALL contain the configured reasoning_effort value

### Requirement: OpenAI completions client passes through reasoning_effort

The `OpenAICompletionsClient` SHALL pass through the `reasoning_effort` parameter to the upstream OpenAI-compatible API without modification.

#### Scenario: Reasoning effort forwarded to OpenAI API
- **WHEN** request body contains `reasoning_effort` parameter
- **THEN** the parameter SHALL be included in the upstream API request
- **AND** the value SHALL NOT be modified

### Requirement: Anthropic messages translator maps reasoning_effort

The `translate_openai_to_anthropic` function SHALL map `reasoning_effort` to Anthropic's `thinking.budget_tokens` format.

#### Scenario: Low reasoning effort mapped
- **WHEN** request contains `reasoning_effort: "low"`
- **THEN** the Anthropic request SHALL contain `thinking: { "budget_tokens": 1024 }`

#### Scenario: Medium reasoning effort mapped
- **WHEN** request contains `reasoning_effort: "medium"`
- **THEN** the Anthropic request SHALL contain `thinking: { "budget_tokens": 4096 }`

#### Scenario: High reasoning effort mapped
- **WHEN** request contains `reasoning_effort: "high"`
- **THEN** the Anthropic request SHALL contain `thinking: { "budget_tokens": 16384 }`

#### Scenario: No reasoning effort parameter
- **WHEN** request does not contain `reasoning_effort` parameter
- **THEN** no `thinking` parameter SHALL be added to Anthropic request

### Requirement: Session acts as HTTP client to psi-ai

The session SHALL act as an HTTP client connecting to psi-ai-* components via Unix socket, forwarding requests using OpenAI chat completion protocol.

#### Scenario: Session forwards request to psi-ai
- **WHEN** session needs to call LLM
- **THEN** session sends HTTP POST request to psi-ai socket path
- **AND** request body SHALL include `reasoning_effort` parameter

#### Scenario: Session receives response from psi-ai
- **WHEN** psi-ai returns chat completion response
- **THEN** session receives the response for processing
