## ADDED Requirements

### Requirement: CLAUDE.md documents session architecture

The `src/psi_agent/session/CLAUDE.md` file SHALL document the overall architecture of the psi-session component, including:
- Component position in the psi-agent architecture (between channel and AI)
- Core responsibilities: message processing, tool execution, workspace management
- Communication protocols: HTTP over Unix socket with OpenAI chat completions format

#### Scenario: Developer understands session role
- **WHEN** a developer reads CLAUDE.md
- **THEN** they understand that session is the orchestrator between channel and AI components

### Requirement: CLAUDE.md documents module structure

The documentation SHALL describe each module file and its responsibility:
- `__init__.py`: Public exports (Session, SessionConfig, SessionRunner, SessionServer, types)
- `config.py`: Configuration dataclass with workspace paths
- `types.py`: Core data structures (ToolSchema, ToolRegistry, History)
- `server.py`: HTTP server handling channel requests
- `runner.py`: Core message processing and tool call handling
- `tool_loader.py`: Dynamic tool loading from workspace
- `tool_executor.py`: Tool execution with parallel support
- `workspace_watcher.py`: Hot-reload change detection
- `schedule.py`: Cron-based task scheduling
- `history.py`: Conversation persistence
- `cli.py`: tyro CLI entry point

#### Scenario: Developer locates functionality
- **WHEN** a developer needs to understand a specific feature
- **THEN** they can find the relevant module from the documentation

### Requirement: CLAUDE.md documents core data structures

The documentation SHALL explain the core data structures defined in `types.py`:
- `ToolSchema`: OpenAI tool schema with execution metadata (name, schema, func, file_hash)
- `ToolRegistry`: Tool management with register/unregister/list operations
- `History`: Conversation message storage with add/clear operations

#### Scenario: Developer understands tool registration
- **WHEN** a developer reads the ToolRegistry documentation
- **THEN** they understand how tools are stored and retrieved

### Requirement: CLAUDE.md documents message processing flow

The documentation SHALL explain the complete message processing flow:
1. Server receives POST /v1/chat/completions from channel
2. Extract last user message from request
3. Check for workspace changes (hot-reload)
4. Build messages with system prompt and history
5. Call psi-ai with streaming enabled
6. Handle tool calls in a loop until complete
7. Return final response to channel

For streaming mode, the documentation SHALL explain:
- SSE chunks are streamed directly to channel
- Tool call info is yielded as reasoning field
- History is persisted after completion

#### Scenario: Developer traces message flow
- **WHEN** a developer reads the message processing section
- **THEN** they can trace a user message through the entire system

### Requirement: CLAUDE.md documents tool system

The documentation SHALL explain the tool system:
- **Discovery**: Scan `tools/*.py` files in workspace
- **Loading**: Dynamic import, parse docstring, generate OpenAI schema
- **Registration**: Store in ToolRegistry with file hash for hot-reload
- **Execution**: Parallel execution via `asyncio.gather()`
- **Schema Generation**: Python type annotations → OpenAI function parameters

The tool function signature SHALL be documented:
```python
async def tool(arg1: type1, arg2: type2 = default) -> ReturnType:
    """Description.

    Args:
        arg1: Description.
        arg2: Description.

    Returns:
        Description.
    """
```

#### Scenario: Developer creates a new tool
- **WHEN** a developer reads the tool documentation
- **THEN** they know how to create a valid tool function

### Requirement: CLAUDE.md documents workspace hot-reload

The documentation SHALL explain the hot-reload mechanism:
- **Detection timing**: Before processing each user message
- **Detection method**: MD5 hash comparison
- **Watched files**:
  - `tools/*.py` — Tool files
  - `skills/*/SKILL.md` — Skill files
  - `schedules/*/TASK.md` — Schedule files
- **Change response**:
  - Tool changes: Update tool registry
  - Skill/schedule changes: Rebuild system prompt
  - Schedule changes: Update schedule executor

The documentation SHALL note that `systems/system.py` is NOT hot-reloadable.

#### Scenario: Developer understands hot-reload scope
- **WHEN** a developer modifies a tool file
- **THEN** they know it will be reloaded without restart

### Requirement: CLAUDE.md documents schedule system

The documentation SHALL explain the schedule system:
- **Schedule format**: `schedules/<name>/TASK.md` with YAML frontmatter
- **Required fields**: `cron` expression
- **Optional fields**: `name`, `description`
- **Execution**: ScheduleExecutor runs tasks at cron times via `process_request()`
- **Hot-reload**: Schedules can be added/modified/removed at runtime

The TASK.md format SHALL be documented:
```markdown
---
name: task-name
description: Task description
cron: "0 9 * * *"
---

Task instruction content...
```

#### Scenario: Developer creates a scheduled task
- **WHEN** a developer reads the schedule documentation
- **THEN** they know how to create a valid TASK.md file

### Requirement: CLAUDE.md documents history persistence

The documentation SHALL explain history management:
- **Storage**: Optional JSON file specified by `history_file` config
- **Loading**: On startup, load from file if exists
- **Persistence**: After each conversation turn
- **Format**: List of message dicts with role and content

#### Scenario: Developer enables history persistence
- **WHEN** a developer wants to persist conversation history
- **THEN** they know to set the `history_file` config option

### Requirement: CLAUDE.md documents System interface

The documentation SHALL explain the workspace System interface:
- **Location**: `systems/system.py`
- **Required class**: `System` with `__init__(workspace: anyio.Path)`
- **Required methods**:
  - `async def build_system_prompt() -> str`
  - `async def compact_history(messages, complete_fn) -> list[dict]`

The documentation SHALL explain that `build_system_prompt()` is called on startup and when skills/schedules change, while `compact_history()` is called before each LLM request.

#### Scenario: Developer customizes system behavior
- **WHEN** a developer wants to customize system prompt or history compaction
- **THEN** they know how to implement the System class

### Requirement: CLAUDE.md documents HTTP interface

The documentation SHALL document the HTTP API:
- **Endpoint**: `POST /v1/chat/completions`
- **Request format**: OpenAI chat completions (model, messages, stream)
- **Response format**: OpenAI chat completions (choices with message)
- **Streaming**: SSE with `data: {...}` chunks and `data: [DONE]`

The documentation SHALL note that:
- Only the last user message is processed
- Tool calls are hidden from channel (filtered in `_filter_for_channel`)
- Model is set to "session" (actual model determined by psi-ai)

#### Scenario: Developer understands channel protocol
- **WHEN** a channel developer reads the documentation
- **THEN** they know the request/response format
