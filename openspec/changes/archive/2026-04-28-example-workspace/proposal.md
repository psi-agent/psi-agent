## Why

psi-agent 需要一个完整的 workspace 示例来验证设计和指导用户。当前 workspace 结构已在 CLAUDE.md 中定义，但缺少具体实现示例和 systems 接口的详细规范。

## What Changes

- 创建示例 workspace 目录结构于 `examples/a-simple-bash-only-workspace/`：
  - `tools/bash.py` — bash 执行工具（async）
  - `skills/hyw/SKILL.md` — 询问问题时使用的 skill
  - `systems/system.py` — system prompt 构建和历史压缩（async）
- 明确所有接口函数必须是 async：
  - `build_system_prompt()` — async，自动扫描 skills 目录，拼接 description 到 system prompt
  - `compact_history()` — async，使用 LLM 摘要压缩过长历史
  - `tool()` — async，所有 tool 函数必须是 async
- 所有 IO 操作（fs、网络、子进程）必须使用 async 生态方法
- 更新 CLAUDE.md 同步 async 接口规范

## Capabilities

### New Capabilities
- `workspace-systems`: systems/system.py 的接口规范（async build_system_prompt, async compact_history）
- `async-tool-interface`: tool 函数必须是 async，使用 asyncio.create_subprocess_exec

### Modified Capabilities
- `claude-md`: 添加 async 接口规范章节

## Impact

- 新增目录：`examples/a-simple-bash-only-workspace/`
- 新增文件：tools/bash.py, skills/hyw/SKILL.md, systems/system.py
- 修改文件：CLAUDE.md（添加 async 规范）
- 示例用于测试 psi-session 和指导用户