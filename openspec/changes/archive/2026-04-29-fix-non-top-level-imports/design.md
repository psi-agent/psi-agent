## Context

Python 编码规范（PEP 8 和项目 CLAUDE.md）要求所有 import 语句放在文件顶部。当前代码库中存在多处非顶级 import，需要分类处理：

**合理的非顶级 import（保留）**：
- 测试代码中测试特定模块的 import

**不合理的非顶级 import（需修复）**：
- 可选依赖 try-import（项目不支持服务降级）
- TYPE_CHECKING 模式下的类型导入
- 避免"假"循环依赖的延迟导入
- 标准库模块在函数内导入
- 第三方库异常类型在错误处理函数内导入

## Goals / Non-Goals

**Goals:**
- 将所有不合理的非顶级 import 移至文件顶级
- 移除 try-except import 包装，改为顶级导入
- 将 TYPE_CHECKING 模式下的导入改为顶级导入
- 将"避免循环依赖"的延迟导入改为顶级导入
- 保持 import 顺序符合项目规范（stdlib → third-party → local）
- 确保修复后代码通过 ruff lint 检查

**Non-Goals:**
- 不修改测试代码中的非顶级 import
- 不改变任何功能行为

## Decisions

### 决策 1：移除 try-except import 包装

**选择**：将 `try: import setproctitle` 改为顶级直接导入。

**理由**：
- 项目不支持服务降级，所有依赖都应正确安装
- try-except 包装增加代码复杂度，无实际收益
- 顶级导入使代码更简洁

**替代方案**：保留 try-except 以支持可选安装。
- 否决原因：项目不支持此模式，依赖缺失应直接报错而非静默降级。

### 决策 2：移除 TYPE_CHECKING 模式

**选择**：将 TYPE_CHECKING 下的导入改为顶级直接导入。

**理由**：
- 多 import 一个类型定义包的开销极小
- 代码一致性更重要，统一顶级导入更简洁
- 避免代码中充斥 `if TYPE_CHECKING:` 条件块

**替代方案**：保留 TYPE_CHECKING 模式以减少运行时开销。
- 否决原因：类型定义模块加载开销可忽略，代码简洁性优先。

### 决策 3：移除"避免循环依赖"的延迟导入

**选择**：将 `runner.py` 中 `_load_single_schedule` 方法内的延迟导入改为顶级导入。

**理由**：
- 经分析，`runner.py` 和 `schedule.py` 之间不存在真正的循环依赖
- `runner.py` 顶级导入 `schedule.py` 的 `Schedule` 和 `ScheduleExecutor`
- `schedule.py` 只在 TYPE_CHECKING 下导入 `SessionRunner`（运行时不导入）
- 延迟导入注释是错误的，应移除

**替代方案**：保留延迟导入以"避免循环依赖"。
- 否决原因：不存在循环依赖，延迟导入无意义。

### 决策 4：标准库模块统一顶级导入

**选择**：将 `asyncio`、`ast` 等标准库模块移至顶级导入。

**理由**：
- 标准库模块无安装依赖问题，顶级导入不会失败
- 符合 PEP 8 规范
- 提高代码可读性，import 语句集中管理

### 决策 5：异常类型顶级导入

**选择**：将 `openai` 和 `anthropic` 库的异常类型移至顶级导入。

**理由**：
- 错误处理是核心功能，这些异常类型在模块加载时就应可用
- 避免每次错误处理时的导入开销
- 符合项目编码规范

## Risks / Trade-offs

**风险 1**：`setproctitle` 未安装时模块加载失败。
- **影响**：用户会立即发现依赖缺失，而非运行时静默降级。
- **缓解**：确保 `setproctitle` 在项目依赖中正确声明。

**风险 2**：修改可能引入语法错误。
- **影响**：低。修改仅涉及 import 语句位置，不改变逻辑。
- **缓解**：运行 `ruff check` 和 `ty check` 验证。