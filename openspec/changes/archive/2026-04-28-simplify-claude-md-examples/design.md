## Context

CLAUDE.md 是项目的主要文档，定义了编码规范和 workspace 结构。当前 systems/ 目录部分包含了约 80 行完整的实现代码，这些代码：
- 可以在 `examples/a-simple-bash-only-workspace/systems/system.py` 找到
- 对于理解规范不是必须的
- 增加了文档的维护负担

## Goals / Non-Goals

**Goals:**
- 精简 systems/ 目录的示例代码
- 保留清晰的规范描述
- 引导开发者查看 examples/ 获取完整实现

**Non-Goals:**
- 不修改 examples/ 目录中的实际代码
- 不改变 systems/system.py 的接口规范

## Decisions

### 精简策略

**决定：** 将 systems/ 目录的示例代码从完整实现精简为规范描述 + 函数签名。

**精简后的内容：**
- 文件名和必要函数签名
- 函数行为描述（不包含代码）
- 引用 examples/ 获取完整实现

**理由：**
- CLAUDE.md 的目的是定义规范，不是提供可复制的代码
- 详细实现应该在 examples/ 中维护
- 减少文档和代码不同步的风险

## Risks / Trade-offs

### 风险：开发者可能不知道去哪里找完整实现

**缓解：**
- 在精简后的描述中明确引用 `examples/a-simple-bash-only-workspace/systems/system.py`
