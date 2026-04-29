## 1. 修复 src/psi_agent/utils/proctitle.py

- [x] 1.1 将 `try: import setproctitle` 改为顶级直接导入 `import setproctitle`
- [x] 1.2 移除 `_HAS_SETPROCTITLE` 变量和相关条件检查
- [x] 1.3 更新 `mask_sensitive_args` 函数，移除 `_HAS_SETPROCTITLE` 检查

## 2. 修复 src/psi_agent/session/schedule.py

- [x] 2.1 将 TYPE_CHECKING 下的 `from psi_agent.session.runner import SessionRunner` 移至顶级
- [x] 2.2 移除 `if TYPE_CHECKING:` 条件块
- [x] 2.3 确保顶级 import 顺序符合规范（stdlib → third-party → local）

**注意**: 经测试验证，runner.py 和 schedule.py 存在真正的循环依赖，因此 schedule.py 必须保留 TYPE_CHECKING 模式。此任务已回滚。

## 3. 修复 src/psi_agent/session/runner.py

- [x] 3.1 将 `_load_single_schedule` 方法内的 `from psi_agent.session.schedule import load_schedule` 移至顶级
- [x] 3.2 与已有的 `from psi_agent.session.schedule import Schedule, ScheduleExecutor` 合并为一行
- [x] 3.3 移除"避免循环依赖"的错误注释

## 4. 修复 src/psi_agent/session/tool_executor.py

- [x] 4.1 将 `import asyncio` 从函数内移至文件顶级，按 import 顺序规范排列

## 5. 修复 src/psi_agent/workspace/snapshot/api.py

- [x] 5.1 将 `import ast` 从函数内移至文件顶级，按 import 顺序规范排列

## 6. 修复 src/psi_agent/workspace/umount/api.py

- [x] 6.1 将 `import ast` 从函数内移至文件顶级，按 import 顺序规范排列

## 7. 修复 src/psi_agent/ai/openai_completions/server.py

- [x] 7.1 将 `from collections.abc import AsyncGenerator` 从函数内移至文件顶级
- [x] 7.2 将 `from typing import cast` 从函数内移至文件顶级
- [x] 7.3 确保顶级 import 顺序符合规范（stdlib → third-party → local）

## 8. 修复 src/psi_agent/ai/anthropic_messages/server.py

- [x] 8.1 将 `from collections.abc import AsyncGenerator` 从函数内移至文件顶级
- [x] 8.2 将 `from typing import cast` 从函数内移至文件顶级
- [x] 8.3 确保顶级 import 顺序符合规范（stdlib → third-party → local）

## 9. 修复 src/psi_agent/ai/openai_completions/client.py

- [x] 9.1 将 `from openai import (AuthenticationError, ...)` 从 `_handle_error` 方法内移至文件顶级
- [x] 9.2 确保顶级 import 顺序符合规范（stdlib → third-party → local）

## 10. 修复 src/psi_agent/ai/anthropic_messages/client.py

- [x] 10.1 将 `from anthropic import (AuthenticationError, ...)` 从 `_handle_error` 方法内移至文件顶级
- [x] 10.2 确保顶级 import 顺序符合规范（stdlib → third-party → local）

## 11. 验证

- [x] 11.1 运行 `ruff check` 确保无 lint 错误
- [x] 11.2 运行 `ty check` 确保无类型错误
- [x] 11.3 运行 `pytest` 确保所有测试通过
