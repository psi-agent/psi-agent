## 1. Core Change Detection Module

- [x] 1.1 Create `src/psi_agent/session/workspace_watcher.py` with `WorkspaceWatcher` class
- [x] 1.2 Implement `compute_file_hash()` function (reuse from tool_loader.py)
- [x] 1.3 Implement `scan_skills_directory()` to scan `skills/*/SKILL.md` files
- [x] 1.4 Implement `scan_schedules_directory()` to scan `schedules/*/TASK.md` files
- [x] 1.5 Implement `WorkspaceWatcher.check_for_changes()` method that returns change summary

## 2. Skill Change Handling

- [x] 2.1 Add skill hash tracking to `WorkspaceWatcher` (dict of skill_name -> hash)
- [x] 2.2 Implement `detect_skill_changes()` to find added/removed/modified skills
- [x] 2.3 Add `skills_changed` flag to change detection result

## 3. Schedule Change Handling

- [x] 3.1 Add schedule hash tracking to `WorkspaceWatcher` (dict of schedule_name -> hash)
- [x] 3.2 Implement `detect_schedule_changes()` to find added/removed/modified schedules
- [x] 3.3 Add `schedules_changed` flag to change detection result
- [x] 3.4 Implement schedule executor update logic in `ScheduleExecutor`

## 4. Integration with SessionRunner

- [x] 4.1 Add `WorkspaceWatcher` instance to `SessionRunner.__init__()`
- [x] 4.2 Initialize watcher in `SessionRunner.__aenter__()`
- [x] 4.3 Call `check_for_changes()` at start of `process_request()`
- [x] 4.4 Rebuild system prompt when skills or schedules changed
- [x] 4.5 Update schedule executor when schedules changed

## 5. Integration with SessionServer

- [x] 5.1 Pass schedule executor reference to session runner
- [x] 5.2 Ensure schedule changes are applied to running executor

## 6. Testing

- [x] 6.1 Write unit tests for `WorkspaceWatcher` hash computation
- [x] 6.2 Write unit tests for skill change detection
- [x] 6.3 Write unit tests for schedule change detection
- [x] 6.4 Write integration test for full hot-reload flow
- [x] 6.5 Run full test suite to ensure no regressions

## 7. Documentation

- [x] 7.1 Update CLAUDE.md with hot-reload behavior documentation
- [x] 7.2 Add logging for all change detection events at INFO level
