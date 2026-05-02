## Context

Channel 组件包含三个子模块：cli、repl、telegram。它们都是 psi-agent 的消息通道，负责与 psi-session 通信。当前三个模块由不同时间开发，存在设计思路、代码风格、日志粒度等方面的不一致。

### 当前架构

```
channel/
├── __init__.py          # 统一入口
├── cli/
│   └── cli.py           # 独立实现，无分离
├── repl/
│   ├── __init__.py
│   ├── cli.py           # CLI 入口
│   ├── config.py        # 配置类
│   ├── client.py        # HTTP 客户端
│   └── repl.py          # REPL 界面
└── telegram/
    ├── __init__.py
    ├── cli.py           # CLI 入口
    ├── config.py        # 配置类
    ├── client.py        # HTTP 客户端
    └── bot.py           # Bot 业务逻辑
```

### 约束

- 保持向后兼容，不改变公共 API
- 遵循 CLAUDE.md 中的编码规范
- 日志粒度遵循项目标准（DEBUG 记录通信细节，INFO 记录生命周期）

## Goals / Non-Goals

**Goals:**

1. 统一三个 channel 子模块的设计模式（三层分离：CLI/Config/Client）
2. 统一日志粒度（DEBUG 记录请求体/响应体，INFO 记录启动/请求接收）
3. 统一错误处理返回格式
4. 统一请求体构建逻辑
5. 统一模块导出风格
6. 统一 async 上下文管理器实现

**Non-Goals:**

1. 不改变功能行为（streaming/non-streaming 逻辑保持不变）
2. 不改变配置参数（CLI 参数保持不变）
3. 不重构 telegram 的复杂流式处理逻辑

## Decisions

### Decision 1: CLI 模块采用三层分离模式

**选择**: 将 cli/cli.py 重构为 cli/cli.py + cli/config.py + cli/client.py

**理由**:
- 与 repl/telegram 保持一致的架构
- 便于测试和维护
- 分离关注点（配置、HTTP 通信、CLI 入口）

**替代方案**:
- 保持现状：cli 模块较简单，不需要分离 → 拒绝，一致性更重要

### Decision 2: 统一请求体构建

**选择**: 所有 channel 请求体统一包含 `"model": "session"` 字段

**理由**:
- 与 OpenAI API 格式保持一致
- telegram 已使用此格式
- 未来可能需要 model 字段进行路由

**替代方案**:
- 移除 model 字段：与 OpenAI API 不一致 → 拒绝

### Decision 3: 统一错误返回格式

**选择**: 使用 `f"Error: <description>"` 格式

**理由**:
- 简洁明了
- 便于用户理解
- 与 cli.py 现有格式一致

### Decision 4: 统一模块导出

**选择**: 所有 channel 子模块导出核心类（Cli/CliClient/CliConfig 等）

**理由**:
- 便于外部使用
- 与 repl 模块一致

### Decision 5: 统一 async 上下文管理器日志

**选择**: `__aexit__` 中记录 connector 关闭日志

**理由**:
- 与 session 关闭日志对称
- 便于调试连接问题

## Risks / Trade-offs

### Risk 1: CLI 重构引入 bug

**缓解**: 保持 send_message 函数签名不变，只重构内部实现

### Risk 2: 请求体变更影响 session 行为

**缓解**: session 应该忽略 model 字段，添加前确认 session 行为

### Risk 3: 错误格式变更影响用户脚本

**缓解**: 错误格式保持 `Error:` 前缀，只调整描述内容