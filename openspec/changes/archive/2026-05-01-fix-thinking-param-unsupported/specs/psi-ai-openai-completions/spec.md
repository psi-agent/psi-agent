## ADDED Requirements

### Requirement: Provider-specific parameter handling

The psi-ai-openai-completions client SHALL handle provider-specific parameters (like `thinking`, `reasoning_effort`) by passing them through the OpenAI SDK's `extra_body` mechanism.

#### Scenario: Thinking parameter does not cause TypeError
- **WHEN** a request is made with `thinking` parameter configured
- **THEN** the client SHALL NOT raise `TypeError: got an unexpected keyword argument 'thinking'`
- **AND** the parameter SHALL be forwarded to the upstream API

#### Scenario: Reasoning effort parameter does not cause TypeError
- **WHEN** a request is made with `reasoning_effort` parameter configured
- **THEN** the client SHALL NOT raise `TypeError`
- **AND** the parameter SHALL be forwarded to the upstream API

#### Scenario: Backward compatibility maintained
- **WHEN** a request is made without any provider-specific parameters
- **THEN** the client behavior SHALL be identical to the previous implementation
- **AND** all standard OpenAI parameters SHALL work as before
