# sensitive-args-masking

Process title masking utility for sensitive CLI arguments.

### Requirement: Process title masking utility

The system SHALL provide a utility function to mask sensitive CLI arguments from the process title.

#### Scenario: Mask sensitive arguments
- **WHEN** `mask_sensitive_args(['api_key', 'token'])` is called
- **THEN** the process title SHALL be modified to hide values of those arguments
- **AND** the process title SHALL show `***` in place of sensitive values

#### Scenario: Graceful fallback on unsupported platforms
- **WHEN** `setproctitle` is not available (ImportError)
- **THEN** the function SHALL log a warning and continue without error
- **AND** the process title SHALL remain unchanged

### Requirement: CLI entry points must mask sensitive arguments

All CLI entry points that accept sensitive credentials SHALL call the masking utility immediately after argument parsing.

#### Scenario: OpenAI completions CLI masks API key
- **WHEN** `psi-ai-openai-completions` is started with `--api-key sk-xxx`
- **THEN** the process title SHALL NOT contain `sk-xxx`
- **AND** the process title SHALL show `--api-key ***`

#### Scenario: Anthropic messages CLI masks API key
- **WHEN** `psi-ai-anthropic-messages` is started with `--api-key sk-ant-xxx`
- **THEN** the process title SHALL NOT contain `sk-ant-xxx`
- **AND** the process title SHALL show `--api-key ***`

#### Scenario: Telegram channel CLI masks token
- **WHEN** `psi-channel-telegram` is started with `--token 123456:ABC`
- **THEN** the process title SHALL NOT contain the token value
- **AND** the process title SHALL show `--token ***`
