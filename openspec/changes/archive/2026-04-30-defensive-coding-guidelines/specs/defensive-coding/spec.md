## ADDED Requirements

### Requirement: External data null-safety

All code that processes data from external sources (LLM responses, user input, API responses) SHALL use defensive null checks before operating on field values.

#### Scenario: String concatenation on potentially null field
- **WHEN** code concatenates a field value that may be null
- **THEN** the code SHALL check `field is not None` before concatenation

#### Scenario: String slicing on potentially null field
- **WHEN** code slices a field value that may be null
- **THEN** the code SHALL check `field is not None` before slicing

#### Scenario: Dictionary access with potentially null value
- **WHEN** code accesses a dictionary field that may have null value
- **THEN** the code SHALL use `dict.get("key")` pattern for safe access

### Requirement: Streaming delta field handling

All streaming delta processing code SHALL handle null values in any field without crashing.

#### Scenario: Delta field is null
- **WHEN** LLM returns streaming delta with any field set to null
- **THEN** the code SHALL skip processing that field without error

#### Scenario: Delta field is missing
- **WHEN** LLM returns streaming delta without a field
- **THEN** the code SHALL skip processing that field without error

#### Scenario: Delta field has valid value
- **WHEN** LLM returns streaming delta with valid field value
- **THEN** the code SHALL process the field normally
