## ADDED Requirements

### Requirement: CLI masks sensitive token from process title

The Telegram channel CLI SHALL mask the `--token` argument from the process title immediately after parsing.

#### Scenario: Token masked in process title
- **WHEN** `psi-channel-telegram` is started with `--token 123456:ABC`
- **THEN** the process title SHALL NOT contain the token value
- **AND** the process title SHALL show `--token ***`
