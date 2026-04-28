## MODIFIED Requirements

### Requirement: Workspace 结构规范
CLAUDE.md SHALL 包含 workspace 目录结构规范：
- tools/: 工具定义（每个 .py 文件一个 tool 函数）
- skills/: 技能定义（每个子目录包含 SKILL.md）
- schedules/: 定时任务（包含 cron 元信息）
- systems/: 系统配置（build_system_prompt, compact_history）

对于 systems/ 目录，CLAUDE.md SHALL 只包含规范描述和函数签名，不包含完整实现代码。完整实现示例 SHALL 在 examples/ 目录中提供。

#### Scenario: 创建新工具
- **WHEN** 开发者需要添加新工具
- **THEN** CLAUDE.md SHALL 指导在 tools/ 目录创建 .py 文件，定义 tool() 函数

#### Scenario: 创建新技能
- **WHEN** 开发者需要添加新技能
- **THEN** CLAUDE.md SHALL 指导在 skills/ 目录创建子目录和 SKILL.md 文件

#### Scenario: 查找完整实现示例
- **WHEN** 开发者需要查看 systems/system.py 的完整实现
- **THEN** CLAUDE.md SHALL 引导开发者查看 examples/a-simple-bash-only-workspace/systems/system.py
