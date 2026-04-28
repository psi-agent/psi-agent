## Context

问题代码在 `runner.py` 第 156 行：
```python
self._system_prompt_cache = asyncio.get_event_loop().run_until_complete(
    load_system_prompt(self.config.workspace_path())
)
```

这在一个已经运行的 async 上下文中调用了 `run_until_complete()`，这是不允许的。

## Goals / Non-Goals

**Goals:**
- 修复 async event loop 错误
- 正确加载 system prompt

**Non-Goals:**
- 改变 system prompt 加载的时机或行为

## Decisions

### 在 `__aenter__` 中预加载 system prompt

**方案：** 将 system prompt 加载移到 `__aenter__` 中，直接 `await` 协程。

**原因：**
- `__aenter__` 是 async 上下文，可以直接 await
- 启动时加载一次，后续请求直接使用缓存
- 避免在请求处理中调用 `run_until_complete`

## Risks / Trade-offs

- 无风险，这是正确的 async 编程模式