## MODIFIED Requirements

### Requirement: Session calls system prompt builder

The session SHALL instantiate the `System` class from workspace systems and call its `build_system_prompt()` instance method. If systems/system.py does not exist or does not export a `System` class, no system prompt is included.

#### Scenario: System class instantiated on startup
- **WHEN** session starts and systems/system.py exists with `System` class
- **THEN** session instantiates `System(workspace_dir)` and stores the instance

#### Scenario: System prompt generated from instance method
- **WHEN** session processes a request and has a `System` instance
- **THEN** session calls `system.build_system_prompt()` and includes result in messages

#### Scenario: No system prompt when systems absent
- **WHEN** workspace does not have systems/system.py or no `System` class
- **THEN** messages do not include a system prompt

### Requirement: Session uses history compaction

The session SHALL call `system.compact_history()` to manage conversation history length, providing a `complete_fn` for LLM-based summarization.

#### Scenario: History compaction before LLM call
- **WHEN** session builds messages for LLM request
- **THEN** session calls `system.compact_history(history, complete_fn, max_tokens)`

#### Scenario: CompleteFn calls psi-ai
- **WHEN** `compact_history` calls the provided `complete_fn`
- **THEN** `complete_fn` sends a single-turn request to psi-ai and returns the response

#### Scenario: Compaction preserves recent context
- **WHEN** history exceeds max_tokens limit
- **THEN** compaction retains recent messages and summarizes older content
