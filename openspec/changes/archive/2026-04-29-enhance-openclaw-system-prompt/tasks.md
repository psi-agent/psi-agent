## 1. Documentation

- [x] 1.1 Create `DIFF.md` describing differences between openclaw-like workspace and real OpenClaw

## 2. Heartbeat Schedule

- [x] 2.1 Create `schedules/heartbeat/` directory
- [x] 2.2 Create `schedules/heartbeat/TASK.md` with cron schedule `*/30 * * * *`
- [x] 2.3 Add task instructions to read HEARTBEAT.md and execute its contents

## 3. System Prompt Builder - Core Sections

- [x] 3.1 Add identity statement at the beginning of system prompt
- [x] 3.2 Add `build_tooling_section()` function for Tooling section
- [x] 3.3 Add `build_tool_call_style_section()` function for Tool Call Style section (without approval handling)
- [x] 3.4 Add `build_execution_bias_section()` function for Execution Bias section
- [x] 3.5 Add `build_safety_section()` function for Safety section
- [x] 3.6 Add `build_workspace_section()` function for Workspace section

## 4. System Prompt Builder - Runtime Info

- [x] 4.1 Add `get_runtime_info()` function using platform and sys modules
- [x] 4.2 Include host, os, arch, Python version, shell in runtime info
- [x] 4.3 Add `build_runtime_section()` function for Runtime section
- [x] 4.4 Add `build_datetime_section()` function for Current Date & Time section

## 5. System Prompt Builder - Skills and Memory

- [x] 5.1 Add `build_skills_section()` function for Skills section
- [x] 5.2 Add `build_memory_section()` function for Memory section
- [x] 5.3 Scan skills/ directory and include skill descriptions in Skills section

## 6. System Prompt Builder - Heartbeats and Silent Replies

- [x] 6.1 Add `build_heartbeats_section()` function for Heartbeats section
- [x] 6.2 Add `build_silent_replies_section()` function for Silent Replies section
- [x] 6.3 Define SILENT_TOKEN constant

## 7. System Prompt Builder - Cache Boundary

- [x] 7.1 Define CACHE_BOUNDARY constant (`<!-- OPENCLAW_CACHE_BOUNDARY -->`)
- [x] 7.2 Insert cache boundary between stable and dynamic sections

## 8. System Prompt Builder - Integration

- [x] 8.1 Refactor `build_system_prompt()` to call all section builder functions
- [x] 8.2 Ensure correct section order: identity, tooling, tool call style, execution bias, safety, workspace, skills, memory, project context, cache boundary, heartbeats, silent replies, date/time, runtime
- [x] 8.3 Pass runtime parameters (model, is_main_session, user_timezone) to builder functions

## 9. Verification

- [x] 9.1 Run `ruff check` on updated system.py
- [x] 9.2 Run `ruff format` on updated system.py
- [x] 9.3 Run `ty check` on updated system.py
- [x] 9.4 Verify system prompt builder produces output with all sections
- [x] 9.5 Verify heartbeat task file is valid
