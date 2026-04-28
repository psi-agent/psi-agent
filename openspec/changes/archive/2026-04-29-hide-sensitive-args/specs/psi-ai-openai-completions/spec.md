## ADDED Requirements

### Requirement: CLI masks sensitive API key from process title

The OpenAI completions CLI SHALL mask the `--api-key` argument from the process title immediately after parsing.

#### Scenario: API key masked in process title
- **WHEN** `psi-ai-openai-completions` is started with `--api-key sk-xxx`
- **THEN** the process title SHALL NOT contain `sk-xxx`
- **AND** the process title SHALL show `--api-key ***`
