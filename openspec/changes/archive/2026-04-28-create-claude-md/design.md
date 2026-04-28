## Context

psi-agent 是一个新的 agent 框架项目，核心理念是可移植性和组件化。目前项目刚初始化，需要建立 CLAUDE.md 文件来指导 AI 助手进行开发。该文件将作为 AI 助手理解项目架构、编码规范和设计原则的首要参考。

## Goals / Non-Goals

**Goals:**
- 创建清晰的 CLAUDE.md 文件，涵盖项目架构、组件职责、编码规范
- 定义四类组件（psi-ai-*, psi-session, psi-channel-*, psi-workspace-*）的设计原则
- 文档化 workspace 目录结构和各部分规范

**Non-Goals:**
- 不包含具体实现细节（这些属于设计文档而非指导文件）
- 不替代正式的技术文档或 API 文档
- 不包含项目依赖或构建配置（这些由其他文件管理）

## Decisions

### 文件结构
CLAUDE.md 将包含以下主要部分：
1. 项目概述：核心理念和设计原则
2. 组件架构：四类组件的职责和接口约定
3. Workspace 结构：目录组织规范
4. 编码规范：Python 代码风格和约定
5. 开发工作流：常用命令和调试方法

### 组件通信模式
各组件通过 Unix socket 进行 IPC 通信，确保松耦合和可移植性。

### 技术栈选择
- 语言：Python
- 包管理：uv
- 通信：Unix socket

## Risks / Trade-offs

- **信息过时风险** → CLAUDE.md 需要随项目演进持续更新
- **过度约束风险** → 保持指导原则级别，不规定具体实现细节