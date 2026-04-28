## 1. Workspace Structure Setup

- [x] 1.1 Create `examples/an-openclaw-like-workspace/` directory structure with `tools/`, `skills/`, `systems/` subdirectories
- [x] 1.2 Create `examples/an-openclaw-like-workspace/openspec/` directory for workspace-specific specs

## 2. Bootstrap Files

- [x] 2.1 Create `AGENTS.md` with OpenClaw-style workspace configuration and behavior rules
- [x] 2.2 Create `SOUL.md` with agent personality and behavioral guidelines
- [x] 2.3 Create `TOOLS.md` with local notes template for environment-specific configuration
- [x] 2.4 Create `IDENTITY.md` with agent identity record template (name, creature, vibe, emoji)
- [x] 2.5 Create `USER.md` with user profile information template
- [x] 2.6 Create `BOOTSTRAP.md` with first-run initialization ritual
- [x] 2.7 Create `HEARTBEAT.md` with periodic check configuration template
- [x] 2.8 Create `MEMORY.md` placeholder for long-term memory storage

## 3. System Prompt Builder

- [x] 3.1 Create `systems/system.py` with `build_system_prompt()` async function
- [x] 3.2 Implement frontmatter stripping helper function `_strip_frontmatter()`
- [x] 3.3 Implement bootstrap file loading with async I/O using `anyio.open_file()`
- [x] 3.4 Implement file loading order: AGENTS.md → SOUL.md → TOOLS.md → IDENTITY.md → USER.md → HEARTBEAT.md → BOOTSTRAP.md → MEMORY.md
- [x] 3.5 Implement MEMORY.md privacy protection (only load in main session)
- [x] 3.6 Implement `compact_history()` placeholder function (keep last N messages)
- [x] 3.7 Add proper error handling for missing files

## 4. Read Tool

- [x] 4.1 Create `tools/read.py` with async `tool()` function
- [x] 4.2 Implement async file reading using `anyio.open_file()`
- [x] 4.3 Add type annotations for `file_path: str` parameter and `str` return type
- [x] 4.4 Add Google-style docstring with Args and Returns sections
- [x] 4.5 Add error handling for file not found and read errors

## 5. Write Tool

- [x] 5.1 Create `tools/write.py` with async `tool()` function
- [x] 5.2 Implement async file writing using `anyio.open_file()`
- [x] 5.3 Add type annotations for `file_path: str` and `content: str` parameters
- [x] 5.4 Add Google-style docstring with Args and Returns sections
- [x] 5.5 Add error handling for write errors

## 6. Edit Tool

- [x] 6.1 Create `tools/edit.py` with async `tool()` function
- [x] 6.2 Implement exact string replacement logic
- [x] 6.3 Add `replace_all: bool = False` parameter for multiple replacements
- [x] 6.4 Add type annotations for all parameters
- [x] 6.5 Add Google-style docstring with Args and Returns sections
- [x] 6.6 Add error handling for no match and multiple matches scenarios

## 7. Bash Tool

- [x] 7.1 Create `tools/bash.py` with async `tool()` function
- [x] 7.2 Implement async subprocess execution using `asyncio.create_subprocess_shell()`
- [x] 7.3 Add `timeout: int = 30` parameter with default timeout
- [x] 7.4 Implement timeout handling using `asyncio.wait_for()`
- [x] 7.5 Add type annotations for all parameters
- [x] 7.6 Add Google-style docstring with Args and Returns sections
- [x] 7.7 Return structured result with stdout, stderr, and exit code

## 8. Verification

- [x] 8.1 Run `ruff check` on all new Python files
- [x] 8.2 Run `ruff format` on all new Python files
- [x] 8.3 Run `ty check` for type checking on all new Python files
- [x] 8.4 Verify all tools can be imported without errors
- [x] 8.5 Verify system prompt builder can load all bootstrap files
