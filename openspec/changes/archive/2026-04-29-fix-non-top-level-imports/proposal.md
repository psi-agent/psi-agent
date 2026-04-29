## Why

Python 编码规范要求所有 import 语句放在文件顶部，但代码库中存在多处非顶级 import。这些非顶级 import 分为两类：

1. **合理的非顶级 import**：测试代码中测试特定模块的 import。这些应该保留。
2. **不合理的非顶级 import**：所有其他情况（包括可选依赖 try-import、TYPE_CHECKING 模式、避免"假"循环依赖、标准库模块、第三方库异常类型等），违反编码规范，应移至顶级。

项目不支持服务降级，不存在 try-import 的场景。多 import 一个包的开销很小，但代码一致性更重要。TYPE_CHECKING 模式虽然常见，但为了代码简洁统一，也应改为顶级导入。

经检查，`runner.py` 和 `schedule.py` 之间不存在真正的循环依赖：
- `runner.py` 顶级导入 `schedule.py` 的 `Schedule` 和 `ScheduleExecutor`
- `schedule.py` 只在 TYPE_CHECKING 下导入 `SessionRunner`（仅用于类型注解）
- 运行时 `schedule.py` 不导入 `runner.py`，因此可以安全地改为顶级导入

本 change 旨在修复所有不合理的非顶级 import，使代码符合 PEP 8 和项目编码规范。

## What Changes

将以下非顶级 import 移至文件顶级：

- `src/psi_agent/utils/proctitle.py`: 将 `try: import setproctitle` 改为顶级导入，移除 try-except 包装
- `src/psi_agent/session/schedule.py`: 将 TYPE_CHECKING 下的 `from psi_agent.session.runner import SessionRunner` 移至顶级
- `src/psi_agent/session/runner.py`: 将 `_load_single_schedule` 方法内的 `from psi_agent.session.schedule import load_schedule` 移至顶级（与已有的 schedule 导入合并）
- `src/psi_agent/session/tool_executor.py`: `import asyncio` 移至顶级
- `src/psi_agent/workspace/snapshot/api.py`: `import ast` 移至顶级
- `src/psi_agent/workspace/umount/api.py`: `import ast` 移至顶级
- `src/psi_agent/ai/openai_completions/server.py`: `from collections.abc import AsyncGenerator` 和 `from typing import cast` 移至顶级
- `src/psi_agent/ai/anthropic_messages/server.py`: `from collections.abc import AsyncGenerator` 和 `from typing import cast` 移至顶级
- `src/psi_agent/ai/openai_completions/client.py`: `from openai import (...)` 异常类型移至顶级
- `src/psi_agent/ai/anthropic_messages/client.py`: `from anthropic import (...)` 异常类型移至顶级

## Capabilities

### New Capabilities

无新能力引入。

### Modified Capabilities

无现有能力的需求变更。此 change 仅涉及代码风格改进，不影响功能行为。

## Impact

**受影响的文件**：
- `src/psi_agent/utils/proctitle.py`
- `src/psi_agent/session/schedule.py`
- `src/psi_agent/session/runner.py`
- `src/psi_agent/session/tool_executor.py`
- `src/psi_agent/workspace/snapshot/api.py`
- `src/psi_agent/workspace/umount/api.py`
- `src/psi_agent/ai/openai_completions/server.py`
- `src/psi_agent/ai/anthropic_messages/server.py`
- `src/psi_agent/ai/openai_completions/client.py`
- `src/psi_agent/ai/anthropic_messages/client.py`

**不受影响的文件**（合理的非顶级 import，保持不变）：
- 所有测试文件 - 测试场景下的合理用法

**兼容性**：无 API 变更，无破坏性变更。