## ADDED Requirements

### Requirement: Import 顺序规范
CLAUDE.md SHALL 规定 Python import 顺序：stdlib → third-party → local。

#### Scenario: AI 生成 import 语句
- **WHEN** AI 助手生成包含 import 的代码
- **THEN** import 语句 SHALL 按照 stdlib、third-party、local 三组顺序排列，每组内按字母排序

### Requirement: Async 上下文管理器规范
CLAUDE.md SHALL 规定 async 上下文管理器的实现模式。

#### Scenario: 实现 async 上下文管理器
- **WHEN** 需要实现 async 上下文管理器（如 `__aenter__`/`__aexit__`）
- **THEN** SHALL 在 `__aexit__` 中将内部资源变量设为 `None` 并记录日志

### Requirement: 错误处理规范
CLAUDE.md SHALL 规定错误处理模式。

#### Scenario: 处理可恢复错误
- **WHEN** 需要处理可能失败的异步操作（如网络请求）
- **THEN** SHALL 使用 try-except，用 loguru 记录错误，返回包含 `error` 和 `status_code` 的 dict

### Requirement: 类型注解规范
CLAUDE.md SHALL 规定类型注解语法。

#### Scenario: 表示可选类型
- **WHEN** 需要表示可选类型（如可能为 None 的变量）
- **THEN** SHALL 使用 `| None` 语法（Python 3.14+），而非 `Optional[X]`

### Requirement: 文档字符串规范
CLAUDE.md SHALL 规定使用 Google style docstring 格式。

#### Scenario: 编写函数文档字符串
- **WHEN** 编写函数或方法的文档字符串
- **THEN** SHALL 使用 Google style 格式，包含简短描述、Args（如有参数）、Returns（如有返回值）、Raises（如有异常）

#### Scenario: 编写模块文档字符串
- **WHEN** 编写模块级文档字符串
- **THEN** SHALL 使用单行或简短描述，说明模块用途