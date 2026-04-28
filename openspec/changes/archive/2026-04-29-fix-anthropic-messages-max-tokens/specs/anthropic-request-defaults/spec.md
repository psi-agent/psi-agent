## ADDED Requirements

### Requirement: Default max_tokens for Anthropic API

The CLI SHALL provide a `max_tokens` parameter with default value 4096. The translator SHALL use this value when `max_tokens` is not provided in the request.

#### Scenario: Request without max_tokens
- **WHEN** an OpenAI-format request is translated to Anthropic format without `max_tokens`
- **THEN** the translated request SHALL include `max_tokens` set to the configured value (default 4096)

#### Scenario: Request with max_tokens provided
- **WHEN** an OpenAI-format request is translated to Anthropic format with `max_tokens` already set
- **THEN** the translator SHALL preserve the provided `max_tokens` value and NOT override it

#### Scenario: CLI with custom max_tokens
- **WHEN** the CLI is started with `--max-tokens 8192`
- **THEN** requests without `max_tokens` SHALL use 8192 as the default

### Requirement: Model placeholder replacement

The client SHALL replace the `"session"` model placeholder with the configured model name.

#### Scenario: Model is session placeholder
- **WHEN** a request has `model` set to `"session"`
- **THEN** the client SHALL replace it with the configured model name

#### Scenario: Model is absent
- **WHEN** a request does not have a `model` field
- **THEN** the client SHALL inject the configured model name

#### Scenario: Model is explicit value
- **WHEN** a request has `model` set to a specific value (not `"session"`)
- **THEN** the client SHALL preserve the provided model value