## ADDED Requirements

### Requirement: Model injection is handled by server only
Model parameter injection SHALL be performed by the server component only, not by the client.

#### Scenario: Client does not inject model
- **WHEN** a request is sent to the client
- **THEN** the client SHALL NOT modify the model parameter

#### Scenario: Server injects model conditionally
- **WHEN** a request arrives at the server
- **THEN** the server SHALL inject the configured model if the request model is None or "session"

### Requirement: Consistent model injection strategy across adapters
Both openai-completions and anthropic-messages adapters SHALL use the same model injection strategy.

#### Scenario: OpenAI adapter conditional injection
- **WHEN** a request arrives at openai-completions server
- **THEN** the server SHALL inject model only if request model is None or "session"

#### Scenario: Anthropic adapter conditional injection
- **WHEN** a request arrives at anthropic-messages server
- **THEN** the server SHALL inject model only if request model is None or "session"

### Requirement: User-specified model is respected
If a request explicitly specifies a model (other than "session"), the adapter SHALL preserve that model.

#### Scenario: User model preserved
- **WHEN** a request contains model="gpt-4o" or model="claude-3-opus"
- **THEN** the adapter SHALL NOT override it with the configured model
