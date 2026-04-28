## ADDED Requirements

### Requirement: Identifiers are preserved in summarization prompts

The summarization prompts SHALL include explicit instructions to preserve critical identifiers exactly as written.

#### Scenario: History summary prompt includes preservation
- **WHEN** _HISTORY_SUMMARY_PROMPT is used for summarization
- **THEN** the prompt SHALL instruct the LLM to preserve:
  - UUIDs and unique identifiers
  - File paths and directory names
  - URLs and API endpoints
  - Hostnames, IPs, and ports
  - Error codes and hash values

#### Scenario: Update summary prompt includes preservation
- **WHEN** _UPDATE_SUMMARIZATION_PROMPT is used for incremental summarization
- **THEN** the prompt SHALL instruct the LLM to preserve identifiers from both previous summary and new messages

### Requirement: Identifiers are preserved exactly without modification

The summarization instructions SHALL require identifiers to be preserved exactly, without shortening, reconstruction, or placeholder substitution.

#### Scenario: UUID preservation
- **WHEN** the original conversation contains UUID "550e8400-e29b-41d4-a716-446655440000"
- **THEN** the summary SHALL contain the exact UUID, not "[UUID]" or similar placeholder

#### Scenario: File path preservation
- **WHEN** the original conversation contains file path "/home/user/project/src/main.py"
- **THEN** the summary SHALL contain the exact path, not "the main file" or similar simplification

#### Scenario: Error code preservation
- **WHEN** the original conversation contains error "ECONNREFUSED 127.0.0.1:8080"
- **THEN** the summary SHALL contain the exact error with IP and port, not "connection error"

### Requirement: Preservation applies to all summarization contexts

Identifier preservation SHALL apply to all summarization scenarios: history summary, turn prefix summary, and incremental update.

#### Scenario: Turn prefix summary preservation
- **WHEN** a turn is split during compaction
- **AND** _TURN_PREFIX_SUMMARY_PROMPT is used
- **THEN** identifiers in the turn prefix SHALL be preserved exactly
