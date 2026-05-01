## Context

在 ai-module-documentation 变更过程中，发生了以下工作流违规：
1. 直接在 main 分支上创建归档提交
2. 直接 push 到 main 分支，绕过了 PR 流程

这暴露了 CLAUDE.md 中缺乏明确的 Git 工作流规范。虽然项目使用了 OpenSpec 工作流，但没有在 CLAUDE.md 中明确强调：
- OpenSpec 变更必须纳入 Git 管理
- 所有变更必须通过 PR 流程
- 禁止直接在 main 分支上工作

## Goals / Non-Goals

**Goals:**
- 在 CLAUDE.md 中添加明确的 Git 工作流规范
- 防止未来再次发生直接 push main 的情况
- 确保 OpenSpec 归档目录始终纳入 Git 管理

**Non-Goals:**
- 不修改现有的 Git 分支保护设置
- 不修改 OpenSpec 工作流本身

## Decisions

### 1. 在 CLAUDE.md 中添加 Git 工作流章节

在现有"开发工作流"章节后添加新的"Git 工作流规范"章节，包含：
- 分支管理规范
- PR 流程规范
- OpenSpec 归档规范

### 2. 强调 OpenSpec 归档必须提交

明确说明 OpenSpec 归档目录（`openspec/changes/archive/`）必须与代码变更一起提交到 Git。

## Risks / Trade-offs

- **风险**: 开发者可能忽略文档中的规范 → 通过 code review 流程检查
- **权衡**: 文档长度增加 → 保持简洁，只添加必要的规范
