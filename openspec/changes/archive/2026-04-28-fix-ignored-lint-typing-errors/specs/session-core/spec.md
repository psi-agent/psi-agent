## ADDED Requirements

### Requirement: Schedule.get_next_run returns properly typed datetime

The `Schedule.get_next_run()` method SHALL return a properly typed `datetime` object without using type ignore comments.

#### Scenario: Type checker accepts get_next_run return type
- **WHEN** running `ty check` on `session/schedule.py`
- **THEN** no type errors are reported for the `get_next_run` method

### Requirement: SessionServer streaming handler uses correct request parameter

The `_handle_streaming()` method in `SessionServer` SHALL pass the correct request object to `response.prepare()`.

#### Scenario: Type checker accepts prepare call
- **WHEN** running `ty check` on `session/server.py`
- **THEN** no type errors are reported for the `response.prepare()` call

#### Scenario: Streaming response works correctly
- **WHEN** a streaming request is sent to the session server
- **THEN** the response is properly prepared and streaming works as expected
