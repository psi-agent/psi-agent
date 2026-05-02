## Why

当前实现对命令行中的 API key 和 token 进行打码处理（`mask_sensitive_args`），但这种方式并不靠谱：
1. 进程启动后到调用 `mask_sensitive_args` 之间存在时间窗口，敏感信息仍可见
2. 增加了代码复杂性，需要维护额外的工具模块
3. 真正的安全应该通过环境变量或配置文件传递敏感信息，而非命令行参数

因此，删除这个功能以简化代码。

## What Changes

- **BREAKING** 删除 `src/psi_agent/utils/` 目录（包含 `proctitle.py` 和 `__init__.py`）
- 删除 `tests/utils/` 目录
- 删除 `src/psi_agent/ai/openai_completions/cli.py` 中的 `mask_sensitive_args` 调用
- 删除 `src/psi_agent/ai/anthropic_messages/cli.py` 中的 `mask_sensitive_args` 调用
- 删除 `src/psi_agent/channel/telegram/cli.py` 中的 `mask_sensitive_args` 调用
- 删除 `setproctitle` 依赖
- 更新相关文档（CLAUDE.md）中的 CLI 安全规范说明

## Capabilities

### New Capabilities

无新增能力。

### Modified Capabilities

- `sensitive-args-masking`: 删除此能力（不再需要）

## Impact

- 影响文件：
  - `src/psi_agent/utils/` 目录（删除）
  - `tests/utils/` 目录（删除）
  - `src/psi_agent/ai/openai_completions/cli.py`（修改）
  - `src/psi_agent/ai/anthropic_messages/cli.py`（修改）
  - `src/psi_agent/channel/telegram/cli.py`（修改）
  - `pyproject.toml`（移除 setproctitle 依赖）
  - 相关 CLAUDE.md 文档
- 不影响运行时行为（打码功能本身不可靠）
- 用户应通过环境变量或配置文件传递敏感信息
