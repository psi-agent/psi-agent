## Why

最近完成了 `pathlib.Path` 到 `anyio.Path` 的迁移工作，但发现 CLAUDE.md 中的 async 规范描述不够明确，导致开发者可能误用同步的 pathlib 接口。同时，在提交代码时遗漏了 OpenSpec 归档目录，需要明确提交规范。

## What Changes

- 在 CLAUDE.md 的 "Async 接口规范" 章节中强调：
  - **禁止使用 `pathlib.Path` 进行文件 IO 操作**
  - **必须使用 `anyio.Path` 的 async 方法**
  - 提供明确的对比示例

- 在 CLAUDE.md 中新增 "Git 提交规范" 章节：
  - **提交时必须包含 OpenSpec 归档目录**（`openspec/changes/archive/`）
  - 说明归档目录的作用和重要性

## Capabilities

### New Capabilities

无新增能力。此变更仅为文档改进。

### Modified Capabilities

无修改的能力。此变更不改变任何代码行为，仅改进文档规范。

## Impact

**受影响的文件**：
- `CLAUDE.md` - 项目开发规范文档

**影响范围**：
- 所有开发者的编码习惯
- Git 提交工作流
- 代码审查标准
