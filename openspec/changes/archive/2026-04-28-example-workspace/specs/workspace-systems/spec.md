## ADDED Requirements

### Requirement: async build_system_prompt 接口
systems/system.py SHALL 提供 async `build_system_prompt()` 函数，返回完整的 system prompt 字符串。

#### Scenario: 构建 system prompt
- **WHEN** psi-session 启动时调用 `await build_system_prompt()`
- **THEN** 函数 SHALL 返回包含 skills description 的 system prompt 字符串

#### Scenario: 自动扫描 skills
- **WHEN** workspace/skills/ 目录包含多个 skill
- **THEN** build_system_prompt() SHALL 使用异步 IO 自动扫描所有 SKILL.md 并提取 description 添加到 system prompt

### Requirement: async compact_history 接口
systems/system.py SHALL 提供 async `compact_history()` 函数，压缩过长对话历史。

#### Scenario: 历史压缩
- **WHEN** 对话历史超过 max_tokens 限制
- **THEN** compact_history() SHALL 使用 LLM 摘要压缩历史，返回精简后的消息列表

### Requirement: async bash tool 接口
tools/bash.py SHALL 提供 async `tool()` 函数，执行 shell 命令。

#### Scenario: 执行命令
- **WHEN** psi-session 调用 `await tool(command="ls -la")`
- **THEN** 函数 SHALL 使用 asyncio.create_subprocess_exec 执行命令并返回输出结果

#### Scenario: 命令超时
- **WHEN** 命令执行超过 timeout 限制
- **THEN** 函数 SHALL 使用 asyncio.wait_for 返回超时错误信息

### Requirement: SKILL.md description 格式
workspace/skills/*/SKILL.md 的 description SHALL 仅说明何时使用 skill，不暴露具体行为细节。

#### Scenario: 懒加载 skill
- **WHEN** psi-session 初始化时读取 skills description
- **THEN** description SHALL 仅包含"何时使用"提示，具体行为在 SKILL.md 正文

#### Scenario: 解析 SKILL.md
- **WHEN** build_system_prompt() 读取 SKILL.md
- **THEN** SHALL 使用异步 IO 正确解析 YAML frontmatter 并提取 description