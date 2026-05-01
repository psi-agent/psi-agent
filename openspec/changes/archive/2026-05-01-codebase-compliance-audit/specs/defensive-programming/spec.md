## ADDED Requirements

### Requirement: Null checks for external data
All data from external sources (LLM responses, user input, API responses) SHALL be validated for null/None values before operations like string concatenation, slicing, or iteration.

#### Scenario: External data field access
- **WHEN** accessing fields from external data (LLM responses, API data)
- **THEN** code SHALL use `dict.get()` with null checks before operations

#### Scenario: String operations on external data
- **WHEN** performing string operations (concatenation, slicing) on external data
- **THEN** code SHALL verify the value is not `None` before the operation

### Requirement: Sensitive argument masking in CLI
All CLI entry points that accept sensitive credentials (API keys, tokens, passwords) SHALL call `mask_sensitive_args()` immediately after argument parsing to hide sensitive values from process title.

#### Scenario: CLI with API key
- **WHEN** a CLI accepts an API key or token parameter
- **THEN** it SHALL call `mask_sensitive_args(["api_key"])` or equivalent at the start of `__call__`

### Requirement: No use of "key in dict" for null value check
Code SHALL NOT use `"key" in dict` pattern to check for null values, as it only checks key existence, not value nullity.

#### Scenario: Checking for null values
- **WHEN** checking if a dictionary value is present and non-null
- **THEN** code SHALL use `dict.get("key") is not None` instead of `"key" in dict`
