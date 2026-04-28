## 1. 创建 CLAUDE.md 基础结构

- [x] 1.1 创建 CLAUDE.md 文件，添加文件头注释
- [x] 1.2 编写项目概述部分，说明核心理念和设计原则

## 2. 编写组件架构文档

- [x] 2.1 编写 psi-ai-* 组件说明（LLM 调用桥梁）
- [x] 2.2 编写 psi-session 组件说明（Session 运行循环）
- [x] 2.3 编写 psi-channel-* 组件说明（消息通道）
- [x] 2.4 编写 psi-workspace-* 组件说明（Workspace 管理）
- [x] 2.5 说明组件间的 IPC 通信机制（Unix socket）

## 3. 编写 Workspace 结构规范

- [x] 3.1 说明 workspace 目录整体结构
- [x] 3.2 编写 tools/ 目录规范（tool 函数定义）
- [x] 3.3 编写 skills/ 目录规范（SKILL.md 格式）
- [x] 3.4 编写 schedules/ 目录规范（cron 任务定义）
- [x] 3.5 编写 systems/ 目录规范（system prompt 和历史压缩）

## 4. 编写编码规范

- [x] 4.1 定义 Python 代码风格（类型注解、命名约定）
- [x] 4.2 定义文档字符串规范
- [x] 4.3 定义 tool 函数规范（入口函数、类型、默认值）

## 5. 添加运行示例

- [x] 5.1 添加 psi-session 启动命令示例
- [x] 5.2 添加 psi-ai-openai-completion 启动命令示例
- [x] 5.3 添加 psi-channel-tui 启动命令示例