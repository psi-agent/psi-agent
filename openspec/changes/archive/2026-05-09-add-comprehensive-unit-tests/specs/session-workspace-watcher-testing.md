## session-workspace-watcher-testing

workspace_watcher 的复合变更和幂等性测试。

### WorkspaceWatcher

- initialize 空 workspace（无 tools/skills/schedules 目录）
- initialize 后连续多次 check_for_changes 无变更返回空 summary
- 同时新增 + 修改 + 删除工具
- 同时新增 + 修改 + 删除 skills
- 同时新增 + 修改 + 删除 schedules
- 新增后立即删除同一工具（两次 check 之间）
- 修改后立即再修改（hash 应更新两次）
- check_for_changes 后内部 hash 已更新，再次 check 不应再报告变更

### scan_tools_directory

- 目录中有子目录（应忽略）
- 目录中有 __pycache__ 目录和 .pyc 文件
- 目录中有 __init__.py（应作为工具扫描）

### scan_skills_directory

- skill 目录中有 SKILL.md 和其他文件
- skill 目录名含特殊字符

### scan_schedules_directory

- schedule 目录中有 TASK.md 和其他文件
- 非目录条目应忽略
