## ADDED Requirements

### Requirement: Provider-specific parameters passed via extra_body

The OpenAI completions client SHALL separate provider-specific parameters from standard OpenAI SDK parameters and pass them via the `extra_body` argument.

#### Scenario: Thinking parameter forwarded correctly
- **WHEN** a request includes `thinking` parameter
- **THEN** the client SHALL pass it via `extra_body` to the SDK
- **AND** the request to upstream API SHALL include `thinking` in the body

#### Scenario: Reasoning effort parameter forwarded correctly
- **WHEN** a request includes `reasoning_effort` parameter
- **THEN** the client SHALL pass it via `extra_body` to the SDK
- **AND** the request to upstream API SHALL include `reasoning_effort` in the body

#### Scenario: Multiple provider parameters forwarded together
- **WHEN** a request includes both `thinking` and `reasoning_effort` parameters
- **THEN** the client SHALL pass both via `extra_body`
- **AND** the upstream request SHALL include both parameters

### Requirement: Standard SDK parameters passed directly

The client SHALL pass known OpenAI SDK parameters directly to `chat.completions.create()`.

#### Scenario: Core parameters passed to SDK
- **WHEN** a request includes standard parameters like `model`, `messages`, `temperature`, `stream`
- **THEN** these parameters SHALL be passed directly to the SDK method
- **AND** NOT included in `extra_body`

### Requirement: No crash on unknown parameters

The client SHALL NOT raise `TypeError` when encountering unknown parameters in the request body.

#### Scenario: Unknown parameter handled gracefully
- **WHEN** a request includes an unknown parameter (not in known SDK parameters list)
- **THEN** the client SHALL pass it via `extra_body`
- **AND** the SDK SHALL NOT raise a `TypeError`

#### Scenario: Empty extra_body when no provider parameters
- **WHEN** a request contains only standard SDK parameters
- **THEN** `extra_body` SHALL be omitted or empty
- **AND** behavior SHALL be identical to current implementation
