## 1. 高影响文件迁移 (session 核心)

- [x] 1.1 迁移 `psi_agent/session/tool_loader.py`
  - 将 `compute_file_hash()` 改为 async
  - 将 `scan_tools_directory()` 改为 async
  - 将 `load_tool_from_file()` 改为 async
  - 将 `load_all_tools()` 改为 async
  - 将 `detect_and_update_tools()` 改为 async
  - 更新所有调用者使用 await

- [x] 1.2 迁移 `psi_agent/session/workspace_watcher.py`
  - 将 `compute_file_hash()` 改为 async
  - 将 `scan_tools_directory()` 改为 async
  - 将 `scan_skills_directory()` 改为 async
  - 将 `scan_schedules_directory()` 改为 async
  - 将 `WorkspaceWatcher.initialize()` 改为 async
  - 将 `WorkspaceWatcher.check_for_changes()` 改为 async
  - 更新所有调用者使用 await

- [x] 1.3 迁移 `psi_agent/session/history.py`
  - 将 `load_history_from_file()` 改为 async
  - 将 `save_history_to_file()` 改为 async
  - 将 `initialize_history()` 改为 async
  - 将 `persist_history()` 改为 async
  - 更新所有调用者使用 await

## 2. 中影响文件迁移 (schedule 和 workspace)

- [x] 2.1 迁移 `psi_agent/session/schedule.py`
  - 将 `load_schedules()` 中的 `iterdir()` 改为 async for
  - 检查并更新 `exists()` 调用

- [x] 2.2 迁移 `psi_agent/session/runner.py`
  - 将 `load_system_prompt()` 中的 `exists()` 改为 async
  - 更新 `_handle_workspace_changes()` 调用

- [x] 2.3 迁移 `psi_agent/workspace/mount/api.py`
  - 将 `mount()` 中的 `exists()`, `is_file()`, `mkdir()` 改为 async
  - 将 `_create_temp_dir()` 改为 async
  - 将 `_mount_squashfs()` 改为 async
  - 将 `_mount_overlayfs()` 改为 async

- [x] 2.4 迁移 `psi_agent/workspace/pack/api.py`
  - 将 `pack()` 中的 `exists()`, `is_dir()`, `mkdir()` 改为 async
  - 将 `_copy_directory()` 改为 async（使用 async for iterdir）
  - 将 `_create_squashfs()` 改为 async

- [x] 2.5 迁移 `psi_agent/workspace/snapshot/api.py`
  - 检查并更新所有 `resolve()`, `exists()` 调用
  - 将 `_read_manifest_from_squashfs()` 改为 async
  - 将 `_extract_squashfs()` 改为 async
  - 将 `_copy_directory()` 改为 async
  - 将 `_create_squashfs()` 改为 async

- [x] 2.6 迁移 `psi_agent/workspace/umount/api.py`
  - 检查并更新所有 `resolve()` 调用
  - 确认 `unlink()`, `rmdir()` 已使用 anyio.Path（部分已使用）
  - 将 `_unmount()` 改为 async
  - 将 `_cleanup_directory()` 改为 async（使用 async for iterdir）

- [x] 2.7 迁移 `psi_agent/workspace/unpack/api.py`
  - 将 `unpack()` 中的 `resolve()`, `exists()` 改为 async

## 3. 低影响文件迁移 (channel 和其他)

- [x] 3.1 迁移 `psi_agent/channel/repl/repl.py`
  - 将 `_ensure_history_dir()` 改为 async
  - 更新 `exists()`, `mkdir()` 调用

- [x] 3.2 迁移 `psi_agent/ai/openai_completions/server.py`
  - 将 socket 文件删除操作改为使用 anyio.Path

## 4. 测试更新

- [x] 4.1 更新 `tests/session/test_tool_loader.py`（如存在）
- [x] 4.2 更新 `tests/session/test_workspace_watcher.py`（如存在）
- [x] 4.3 更新 `tests/session/test_history.py`（如存在）
- [x] 4.4 更新其他受影响的测试文件

## 5. 验证

- [x] 5.1 运行 `ruff check` 确保无 lint 错误
- [x] 5.2 运行 `ruff format` 确保格式正确
- [x] 5.3 运行 `ty check` 确保类型检查通过
- [x] 5.4 运行所有测试确保无回归