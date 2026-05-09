## session-config-testing

SessionConfig 辅助方法的完整测试。

### SessionConfig

- `history_file_path`: workspace 为 None 时返回 None；workspace 有值时返回 workspace / "history.json" 路径
- `tools_dir`: 返回 workspace / "tools" 路径
- `systems_dir`: 返回 workspace / "systems" 路径
- `skills_dir`: 返回 workspace / "skills" 路径
- `schedules_dir`: 返回 workspace / "schedules" 路径
- workspace 路径含特殊字符（空格、中文）时的路径拼接正确性
