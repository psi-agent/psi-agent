## ADDED Requirements

### Requirement: Read tool reads file content

The read tool SHALL read the content of a specified file asynchronously and return it as a string.

#### Scenario: Read existing file
- **WHEN** the read tool is called with a valid file path
- **THEN** the tool returns the file content as a string

#### Scenario: Read non-existent file
- **WHEN** the read tool is called with a path to a file that does not exist
- **THEN** the tool returns an error message indicating the file does not exist

#### Scenario: Async file reading
- **WHEN** the read tool reads a file
- **THEN** the operation uses async I/O (anyio.open_file) to avoid blocking the event loop

### Requirement: Write tool creates or overwrites file

The write tool SHALL write content to a specified file asynchronously, creating the file if it does not exist or overwriting it if it does.

#### Scenario: Write to new file
- **WHEN** the write tool is called with a path to a non-existent file
- **THEN** the tool creates the file and writes the specified content

#### Scenario: Write to existing file
- **WHEN** the write tool is called with a path to an existing file
- **THEN** the tool overwrites the file with the specified content

#### Scenario: Async file writing
- **WHEN** the write tool writes to a file
- **THEN** the operation uses async I/O (anyio.open_file) to avoid blocking the event loop

### Requirement: Edit tool performs exact string replacement

The edit tool SHALL read a file, replace an exact string match with new content, and write the result back asynchronously.

#### Scenario: Edit with exact match
- **WHEN** the edit tool is called with an old_string that exactly matches content in the file
- **THEN** the tool replaces the old_string with the new_string and writes the modified content back

#### Scenario: Edit with no match
- **WHEN** the edit tool is called with an old_string that does not match any content in the file
- **THEN** the tool returns an error indicating no match was found and does not modify the file

#### Scenario: Edit with multiple matches
- **WHEN** the edit tool is called with replace_all=true and the old_string appears multiple times
- **THEN** the tool replaces all occurrences of the old_string with the new_string

#### Scenario: Edit without replace_all and multiple matches
- **WHEN** the edit tool is called with replace_all=false (default) and the old_string appears multiple times
- **THEN** the tool returns an error indicating multiple matches were found

### Requirement: Bash tool executes shell commands

The bash tool SHALL execute shell commands asynchronously with timeout support and return the output.

#### Scenario: Execute successful command
- **WHEN** the bash tool is called with a valid shell command
- **THEN** the tool executes the command and returns stdout, stderr, and exit code

#### Scenario: Execute command with timeout
- **WHEN** the bash tool is called with a timeout parameter and the command exceeds the timeout
- **THEN** the tool terminates the process and returns a timeout error

#### Scenario: Async command execution
- **WHEN** the bash tool executes a command
- **THEN** the operation uses async subprocess (asyncio.create_subprocess_exec or create_subprocess_shell) to avoid blocking the event loop

### Requirement: All tools use async entry function

All tools SHALL define an async function named `tool` as the entry point, following psi-agent conventions.

#### Scenario: Tool function is async
- **WHEN** a tool file is loaded by psi-agent
- **THEN** the entry function is named `tool` and is an async function

### Requirement: Tools have type annotations

All tools SHALL use type annotations for all parameters and return values.

#### Scenario: Type annotations present
- **WHEN** a tool function is defined
- **THEN** all parameters have type annotations and the return type is specified

### Requirement: Tools have Google-style docstrings

All tools SHALL have Google-style docstrings describing the function, parameters, and return values.

#### Scenario: Docstring format
- **WHEN** a tool function is defined
- **THEN** the docstring follows Google style with Args and Returns sections