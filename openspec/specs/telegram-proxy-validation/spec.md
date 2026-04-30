## Purpose

Provide clear error messages and logging for Telegram proxy configuration issues.

## Requirements

### Requirement: Telegram channel provides clear error messages for proxy misconfiguration

The Telegram channel SHALL provide clear, actionable error messages when proxy configuration fails due to missing dependencies or invalid configuration.

#### Scenario: Missing socksio dependency error message
- **WHEN** SOCKS5 proxy is configured but `socksio` is not installed
- **THEN** the error message SHALL include:
  - A clear indication that SOCKS5 proxy support requires additional dependencies
  - The exact command to install the dependency
  - The proxy URL that caused the error (with credentials masked)

#### Scenario: Invalid proxy URL format
- **WHEN** an invalid proxy URL is provided
- **THEN** the error message SHALL indicate the URL format is invalid
- **AND** the error message SHALL show the expected format

### Requirement: Telegram channel logs proxy configuration at startup

The Telegram channel SHALL log proxy configuration (with credentials masked) at startup for debugging purposes.

#### Scenario: Proxy configuration logged at startup
- **WHEN** a proxy URL is provided
- **THEN** the bot SHALL log the proxy host and port (without credentials) at INFO level
- **AND** credentials in the proxy URL SHALL be replaced with `***`
