## Why

psi-agent 是一个以可移植性和组件化为核心理念的 agent 框架。为了确保未来开发者（包括 AI 助手如 Claude）能够准确理解项目架构和编码规范，需要创建一个 CLAUDE.md 文件作为项目指南，使 AI 助手能够遵循项目的设计原则进行开发。

## What Changes

- 创建 CLAUDE.md 文件，包含项目架构说明、组件结构、编码规范等指导内容
- 定义四类组件（psi-ai-*, psi-session, psi-channel-*, psi-workspace-*）的职责和接口约定
- 文档化 workspace 目录结构和各组成部分的规范

## Capabilities

### New Capabilities
- `claude-md`: 项目级 AI 指导文件，包含架构概览、组件设计原则、编码规范等

### Modified Capabilities

(None - this is a new project)

## Impact

- 影响范围：项目根目录新增 CLAUDE.md
- 受益者：所有使用 AI 辅助开发的贡献者
- 依赖关系：无