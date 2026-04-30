## Context

当前测试覆盖率 79%，主要问题集中在：
- CLI 入口点模块（`__main__.py` 0%，各组件 CLI 52-69%）
- workspace 操作 API（`snapshot/api.py` 33%，`mount/api.py` 41%）
- schedule 执行器（54%）

这些模块缺乏测试的原因：
- CLI 模块需要模拟命令行参数和进程行为
- workspace 操作涉及 root 权限的 mount/umount 操作
- schedule 执行器涉及异步定时任务和文件监听

## Goals / Non-Goals

**Goals:**
- 将整体测试覆盖率从 79% 提升至 90%+
- 为所有覆盖率低于 60% 的模块添加测试
- 确保所有测试可重复执行、无外部依赖

**Non-Goals:**
- 不修改生产代码逻辑
- 不改变现有 API 接口
- 不引入新的测试框架（继续使用 pytest）

## Decisions

### 测试策略

**决策：使用 pytest + pytest-asyncio + pytest-mock**

理由：
- 项目已使用 pytest，保持一致性
- pytest-asyncio 支持 async 函数测试
- pytest-mock 用于模拟外部依赖（文件系统、子进程、网络）

### CLI 测试方法

**决策：使用 tyro.testing 通过函数调用测试 CLI 逻辑**

理由：
- tyro CLI 是 Python API 的直接封装
- 直接调用 Python 函数比 subprocess 更快、更可靠
- 可精确控制输入参数和验证输出

替代方案：使用 subprocess 调用实际命令
- 缺点：启动慢、难以捕获输出、需要处理进程生命周期

### Workspace 操作测试

**决策：使用 mock 模拟 subprocess 调用**

理由：
- mount/umount 需要 root 权限
- squashfs 操作需要特定文件系统支持
- mock 可验证命令参数正确性，无需实际执行

替代方案：使用 Docker 容器提供 root 环境
- 缺点：CI 复杂度增加、执行时间长

### Schedule 执行器测试

**决策：使用时间控制和 mock 验证定时触发**

理由：
- 实际等待 cron 触发不现实
- 可通过 `asyncio.sleep` 和时间模拟控制执行时机
- 验证任务加载、解析、触发逻辑

## Risks / Trade-offs

- **Mock 过度使用**：测试可能无法发现实际运行时问题 → 保持核心逻辑测试使用真实实现
- **覆盖率数字陷阱**：高覆盖率不等于高质量 → 关注边界条件和错误处理
- **CI 时间增加**：更多测试意味着更长运行时间 → 保持测试高效，避免不必要的等待
