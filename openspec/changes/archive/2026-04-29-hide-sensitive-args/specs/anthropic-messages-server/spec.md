## ADDED Requirements

### Requirement: CLI masks sensitive API key from process title

The Anthropic messages CLI SHALL mask the `--api-key` argument from the process title immediately after parsing.

#### Scenario: API key masked in process title
- **WHEN** `psi-ai-anthropic-messages` is started with `--api-key sk-ant-xxx`
- **THEN** the process title SHALL NOT contain `sk-ant-xxx`
- **AND** the process title SHALL show `--api-key ***`
