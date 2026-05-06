## Why

Channel 子包缺乏详细的 CLAUDE.md 文档，导致 AI 助手在理解和维护代码时需要反复阅读源码。为 channel 包及其子包（cli、repl、telegram）编写全面的文档，记录设计思路、代码规范、接口定义和实现细节，提高代码可维护性和 AI 辅助开发效率。

## What Changes

### 新增文档文件

- `src/psi_agent/channel/CLAUDE.md` — Channel 包总览文档
- `src/psi_agent/channel/cli/CLAUDE.md` — CLI 子包文档
- `src/psi_agent/channel/repl/CLAUDE.md` — REPL 子包文档
- `src/psi_agent/channel/telegram/CLAUDE.md` — Telegram 子包文档

### 文档内容

每个 CLAUDE.md 将包含：
- 模块概述和职责
- 架构设计（三层分离模式）
- 核心类和接口定义
- 配置说明
- 日志规范
- 错误处理模式
- 测试指南
- 使用示例

## Capabilities

### New Capabilities

- `channel-documentation`: Channel 包的完整文档规范，包括架构设计、接口定义、代码规范等

### Modified Capabilities

无（此变更仅添加文档，不修改任何代码行为）

## Impact

- 新增 4 个 CLAUDE.md 文档文件
- 不影响现有代码功能
- 提高 AI 辅助开发效率
- 便于新开发者理解代码结构
