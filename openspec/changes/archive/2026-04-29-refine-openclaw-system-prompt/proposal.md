## Why

当前的 openclaw-like workspace 的 system prompt builder 有几个需要改进的地方：
1. 身份声明仍然使用 "OpenClaw"，应该改为 "psi-agent"
2. Skills 部分缺少速率限制指导，这在调用外部 API 时很重要
3. HEARTBEAT.md 应该放在 cache boundary 之后（动态部分），而不是和其他 bootstrap 文件一起放在稳定部分

## What Changes

- 修改身份声明：从 "You are a personal assistant running inside OpenClaw." 改为 "You are a personal assistant running inside psi-agent."
- 在 Skills 部分添加速率限制指导
- 将 HEARTBEAT.md 从稳定上下文移到动态上下文（cache boundary 之后）

## Capabilities

### New Capabilities

无新增 capability。

### Modified Capabilities

- `openclaw-system-prompt`: 修改身份声明，添加 Skills 速率限制指导
- `openclaw-system-prompt-sections`: 添加动态上下文文件处理要求

## Impact

- `examples/an-openclaw-like-workspace/systems/system.py` - 修改 system prompt builder
- `examples/an-openclaw-like-workspace/DIFF.md` - 更新差异说明
