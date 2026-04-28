## ADDED Requirements

### Requirement: Tools are scanned at session startup

The session SHALL scan the workspace tools directory at startup and register all tool functions.

#### Scenario: Tools directory scanned on startup
- **WHEN** session starts with a workspace path
- **THEN** all .py files in tools/ directory are scanned for tool functions

#### Scenario: Tool function registered with schema
- **WHEN** a valid tool function is found
- **THEN** the tool is registered with OpenAI tool schema derived from function signature and docstring

### Requirement: Tool directory changes are detected

The session SHALL check for tool directory changes (new files, modified files) on each request and update the registry accordingly.

#### Scenario: New tool detected on request
- **WHEN** a new .py file appears in tools/ directory
- **THEN** the new tool is loaded and registered before processing the request

#### Scenario: Modified tool reloaded on request
- **WHEN** an existing tool file hash changes
- **THEN** the tool is reloaded and schema updated

### Requirement: Tool functions are executed asynchronously

The session SHALL execute tool functions as async coroutines, passing parameters from tool_call.

#### Scenario: Tool executed with correct parameters
- **WHEN** LLM requests tool execution with specific arguments
- **THEN** the tool function is called with those arguments

#### Scenario: Tool returns result to session
- **WHEN** tool execution completes
- **THEN** the result is formatted as tool message for LLM

### Requirement: Tool functions guarantee return

Tool functions SHALL always return a result. Error handling and timeout are the responsibility of workspace designers.

#### Scenario: Tool returns result
- **WHEN** tool execution is called
- **THEN** tool function returns a value (success or error message as designed by workspace)

### Requirement: Tool schema is generated from function definition

The session SHALL generate OpenAI tool schema from the tool function's type annotations and Google-style docstring.

#### Scenario: Schema includes function description
- **WHEN** tool has docstring with description
- **THEN** schema description includes that text

#### Scenario: Schema includes parameter descriptions
- **WHEN** tool has Args section in docstring
- **THEN** schema parameters include those descriptions