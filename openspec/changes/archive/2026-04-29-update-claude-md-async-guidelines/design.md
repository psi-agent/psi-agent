## Context

CLAUDE.md 是项目的开发规范文档，指导所有开发者的编码行为。当前文档存在两个问题：

1. **Async 规范不够明确**：虽然提到了"所有 IO 操作必须使用 async 生态方法"，但没有明确禁止 `pathlib.Path`，导致开发者可能误用。

2. **缺少 Git 提交规范**：没有说明 OpenSpec 归档目录需要一同提交，导致归档信息丢失。

## Goals / Non-Goals

**Goals:**
- 明确禁止使用 `pathlib.Path` 进行文件 IO 操作
- 明确要求使用 `anyio.Path` 的 async 方法
- 新增 Git 提交规范，要求包含 OpenSpec 归档目录
- 提供清晰的示例和对比

**Non-Goals:**
- 不修改任何代码
- 不改变项目架构
- 不引入新的工具或依赖

## Decisions

### Decision 1: 在 "Async 接口规范" 章节中添加禁止条款

**选择**: 在现有章节中添加明确的禁止条款和示例

**理由**:
- 保持文档结构一致
- 开发者习惯在现有章节查找相关规范
- 通过对比示例增强理解

**内容**:
```markdown
**禁止使用 `pathlib.Path` 进行文件 IO 操作** — 所有文件操作方法（`read_text()`, `exists()`, `iterdir()` 等）都是同步的，会阻塞事件循环。必须使用 `anyio.Path` 的 async 方法：`await anyio.Path(path).read_text()`、`await anyio.Path(path).exists()`、`async for p in anyio.Path(path).iterdir()` 等。`pathlib.Path` 可用于类型注解和路径拼接（无 IO 操作时）。
```

### Decision 2: 新增 "Git 提交规范" 章节

**选择**: 作为独立章节添加在文档末尾

**理由**:
- Git 提交规范是独立的工作流程
- 便于开发者快速定位
- 未来可扩展其他 Git 相关规范

**内容**:
```markdown
## Git 提交规范

使用 OpenSpec 工作流完成变更后，归档目录（`openspec/changes/archive/YYYY-MM-DD-<change-name>/`）必须一同提交，以便追溯变更动机和设计决策。
```

## Risks / Trade-offs

### Risk 1: 开发者可能忽略新规范

**风险**: 文档更新后，开发者可能不阅读或忽略新规范

**缓解**: 
- 在 PR 审查时检查是否使用了 pathlib.Path
- 使用 ruff 规则检测（未来可考虑）

### Risk 2: 现有代码可能不符合新规范

**风险**: 文档更新后，现有代码可能被视为"违规"

**缓解**: 
- 说明此规范是对新代码的要求
- 已完成的 pathlib → anyio 迁移已符合规范
