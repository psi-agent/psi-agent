## Why

在 ai-module-documentation 变更过程中，我错误地直接在 main 分支上工作并直接 push 到 main，这违反了项目的工作流规范。为了防止未来再次发生类似错误，需要在主 CLAUDE.md 中明确强调 Git 工作流规范。

## What Changes

- 在 `CLAUDE.md` 中添加 Git 工作流规范章节
- 强调 OpenSpec 变更必须纳入 Git 管理
- 强调禁止直接在 main 分支上工作
- 强调禁止直接 push 到 main 分支

## Capabilities

### New Capabilities

- `git-workflow-compliance`: Git 工作流规范，确保所有变更通过 PR 流程

### Modified Capabilities

None

## Impact

- `CLAUDE.md` — 添加 Git 工作流规范章节
- 所有开发者 — 需要遵循新的工作流规范
