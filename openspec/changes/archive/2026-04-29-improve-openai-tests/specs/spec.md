## ADDED Requirements

### Requirement: Mock-based testing pattern

The OpenAI completions client tests SHALL use `unittest.mock.patch` to mock the `AsyncOpenAI` SDK, consistent with the Anthropic tests pattern.

#### Scenario: Mock SDK for non-streaming test
- **WHEN** testing non-streaming requests
- **THEN** the `AsyncOpenAI` client SHALL be patched and mocked
- **AND** no real HTTP requests SHALL be made

#### Scenario: Mock SDK for streaming test
- **WHEN** testing streaming requests
- **THEN** the `AsyncOpenAI` client SHALL be patched and mocked
- **AND** mock streaming responses SHALL be returned

### Requirement: Test coverage parity

The OpenAI tests SHALL have coverage at least equal to the Anthropic tests.

#### Scenario: Test all error types
- **WHEN** running the test suite
- **THEN** tests SHALL cover authentication, rate limit, connection, and timeout errors

#### Scenario: Test model injection
- **WHEN** a request is made without a model
- **THEN** the test SHALL verify the configured model is injected
