## Why

在分析 psi-ai 模块的两个组件（openai-completions 和 anthropic-messages）时，发现存在设计不一致和代码冗余的问题，主要表现在 model 参数处理逻辑上。

## What Changes

- 统一 model 参数处理逻辑，消除 server 和 client 之间的冗余检查
- 统一两个适配器的 model 处理策略

## 问题分析

### 1. openai-completions 的 model 处理

**server.py 第 59 行：**
```python
body["model"] = self.config.model  # 强制覆盖
```

**client.py 第 120-123 行：**
```python
model = request_body.get("model")
if model is None:
    request_body["model"] = self.config.model  # 只在缺失时注入
```

**问题**：server 强制覆盖 model，导致 client 中的条件注入逻辑永远不会生效。这是代码冗余。

### 2. anthropic-messages 的 model 处理

**server.py 第 86-89 行：**
```python
model = request_body.get("model")
if model is None or model == "session":
    request_body["model"] = self.config.model  # 条件注入
```

**client.py 第 86-89 行：**
```python
model = request_body.get("model")
if model is None or model == "session":
    request_body["model"] = self.config.model  # 条件注入
```

**问题**：server 和 client 都有相同的条件注入逻辑，存在重复检查。

### 3. 两个适配器的策略不一致

| 适配器 | Server 行为 | Client 行为 | 实际效果 |
|--------|------------|-------------|----------|
| openai-completions | 强制覆盖 | 条件注入 | Server 覆盖生效，Client 逻辑冗余 |
| anthropic-messages | 条件注入 | 条件注入 | 重复检查 |

## Capabilities

### New Capabilities

- `ai-module-model-handling`: AI 模块 model 参数处理规范

### Modified Capabilities

None

## Impact

- `src/psi_agent/ai/openai_completions/client.py` — 移除冗余的 model 注入逻辑
- `src/psi_agent/ai/anthropic_messages/client.py` — 移除冗余的 model 注入逻辑
- 两个适配器的行为更加一致和可预测
