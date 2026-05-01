## Context

psi-ai 模块包含两个 LLM 提供商适配器，它们应该遵循统一的设计模式。当前存在以下问题：

1. **model 参数处理不一致**：openai-completions 强制覆盖，anthropic-messages 条件注入
2. **代码冗余**：server 和 client 都有 model 注入逻辑，导致重复检查或死代码

## Goals / Non-Goals

**Goals:**
- 统一两个适配器的 model 参数处理策略
- 消除 server 和 client 之间的冗余代码
- 保持现有行为不变（server 负责注入 model）

**Non-Goals:**
- 不改变 API 行为
- 不修改配置结构

## Decisions

### 1. Model 注入由 Server 负责

**理由**：
- Server 是请求的入口点，应该负责参数预处理
- Client 应该是纯粹的 API 调用层，不应该有业务逻辑

**决策**：
- 移除两个 client 中的 model 注入逻辑
- Server 统一使用条件注入策略（缺失或为 "session" 时注入）

### 2. 统一条件注入策略

**openai-completions 当前行为**：强制覆盖 model

**问题**：这会忽略用户在请求中指定的 model，可能不是预期行为

**决策**：改为条件注入，与 anthropic-messages 保持一致

```python
# 统一的注入逻辑
model = body.get("model")
if model is None or model == "session":
    body["model"] = self.config.model
```

## Risks / Trade-offs

- **风险**：改变 openai-completions 的行为可能影响现有用户
- **缓解**：大多数情况下用户不指定 model，行为不变；如果用户指定了 model，现在会尊重用户选择，这是更合理的行为
