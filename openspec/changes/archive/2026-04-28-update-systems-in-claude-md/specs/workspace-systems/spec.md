## MODIFIED Requirements

### Requirement: systems/ 目录规范
systems/system.py SHALL 提供两个 async 函数：`build_system_prompt()` 和 `compact_history()`。

#### Scenario: 构造 system prompt
- **WHEN** psi-session 启动时调用 `await build_system_prompt()`
- **THEN** 函数 SHALL 返回包含 skills description 的 system prompt 字符串

#### Scenario: 自动扫描 skills
- **WHEN** workspace/skills/ 目录包含多个 skill
- **THEN** build_system_prompt() SHALL 使用异步 IO 自动扫描所有 SKILL.md 并提取 description 添加到 system prompt

#### Scenario: 历史压缩
- **WHEN** 对话历史超过 max_tokens 限制
- **THEN** compact_history() SHALL 使用 LLM 摘要压缩历史，返回精简后的消息列表

#### Scenario: 函数签名
- **WHEN** 定义 systems/system.py 中的函数
- **THEN** SHALL 使用以下签名：
  - `async def build_system_prompt() -> str`
  - `async def compact_history(history: list[dict[str, str]], max_tokens: int = 4000) -> list[dict[str, str]]`
