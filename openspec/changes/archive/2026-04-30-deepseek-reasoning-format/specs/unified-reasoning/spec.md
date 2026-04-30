## MODIFIED Requirements

### Requirement: Session adds reasoning_effort to AI requests

The session SHALL include both `thinking: {"type": "enabled"}` and `reasoning_effort` parameter in all requests sent to AI components.

#### Scenario: Thinking toggle included in request
- **WHEN** session sends a request to AI component
- **THEN** the request body SHALL contain `thinking: {"type": "enabled"}`

#### Scenario: Reasoning effort included in request
- **WHEN** session sends a request to AI component
- **THEN** the request body SHALL contain `reasoning_effort` parameter
- **AND** the default value SHALL be "medium"

#### Scenario: Reasoning effort configurable
- **WHEN** session is configured with a specific reasoning_effort level
- **THEN** the request body SHALL contain the configured reasoning_effort value

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

## REMOVED Requirements

### Requirement: Budget tokens mapping
**Reason**: DeepSeek uses `output_config.effort` format, not `thinking.budget_tokens`
**Migration**: The `REASONING_EFFORT_TO_BUDGET_TOKENS` constant is no longer used
