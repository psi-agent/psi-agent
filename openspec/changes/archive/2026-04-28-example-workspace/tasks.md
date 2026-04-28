## 1. 目录结构创建

- [x] 1.1 创建 examples/a-simple-bash-only-workspace/ 目录
- [x] 1.2 创建 examples/a-simple-bash-only-workspace/tools/ 目录
- [x] 1.3 创建 examples/a-simple-bash-only-workspace/skills/hyw/ 目录
- [x] 1.4 创建 examples/a-simple-bash-only-workspace/systems/ 目录

## 2. async bash tool 实现（需重写）

- [x] 2.1 重写 examples/a-simple-bash-only-workspace/tools/bash.py 为 async
- [x] 2.2 实现 `async def tool(command: str, timeout: int = 30) -> str`
- [x] 2.3 使用 `asyncio.create_subprocess_shell` 执行命令
- [x] 2.4 使用 `asyncio.wait_for(process.communicate(), timeout)` 处理超时
- [x] 2.5 编写 Google style docstring

## 3. hyw skill 实现（需修改 description）

- [x] 3.1 修改 examples/a-simple-bash-only-workspace/skills/hyw/SKILL.md
- [x] 3.2 description 改为 "Use this skill when asking the user questions."
- [x] 3.3 具体行为（添加"何意味？"前缀）移到正文，不暴露在 description

## 4. async systems 实现（需重写）

- [x] 4.1 重写 examples/a-simple-bash-only-workspace/systems/system.py 为 async
- [x] 4.2 实现 `async def build_system_prompt()` 函数
- [x] 4.3 使用 Path.read_text 同步读取（标注了 aiofiles 替代方案）
- [x] 4.4 实现 YAML frontmatter 解析提取 description
- [x] 4.5 实现 `async def compact_history()` 函数框架
- [x] 4.6 编写 Google style docstring

## 5. CLAUDE.md 更新

- [x] 5.1 添加 async 接口规范章节
- [x] 5.2 说明所有接口函数必须是 async
- [x] 5.3 说明 IO 操作必须使用 async 生态（aiofiles, asyncio.create_subprocess_exec）

## 6. 质量检查

- [x] 6.1 运行 `ruff format` 格式化代码
- [x] 6.2 运行 `ruff check` lint 检查
- [x] 6.3 运行 `ty check` typing 检查
- [x] 6.4 验证目录结构完整