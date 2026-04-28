# claude-md

项目级 AI 指导文件规范。

### Requirement: CLAUDE.md 文件存在
CLAUDE.md 文件 SHALL 存在于项目根目录，作为 AI 助手的首要指导文件。

#### Scenario: AI 助手读取项目指导
- **WHEN** AI 助手开始工作于 psi-agent 项目
- **THEN** AI 助手 SHALL 读取 CLAUDE.md 文件获取项目架构和编码规范

### Requirement: 项目概述部分
CLAUDE.md SHALL 包含项目概述部分，说明 psi-agent 的核心理念（可移植性、组件化）和设计原则。

#### Scenario: 理解项目核心理念
- **WHEN** 开发者或 AI 助手阅读 CLAUDE.md
- **THEN** 文件 SHALL 清晰说明可移植性和组件化两大原则

### Requirement: 组件架构说明
CLAUDE.md SHALL 包含四类组件的架构说明：
- psi-ai-*: LLM 调用桥梁
- psi-session: Session 运行循环
- psi-channel-*: 消息通道
- psi-workspace-*: Workspace 管理

#### Scenario: 理解组件职责
- **WHEN** 需要开发新组件或修改现有组件
- **THEN** CLAUDE.md SHALL 提供各类组件的职责边界和接口约定

### Requirement: Workspace 结构规范
CLAUDE.md SHALL 包含 workspace 目录结构规范：
- tools/: 工具定义（每个 .py 文件一个 tool 函数）
- skills/: 技能定义（每个子目录包含 SKILL.md）
- schedules/: 定时任务（包含 cron 元信息）
- systems/: 系统配置（build_system_prompt, compact_history）

对于 systems/ 目录，CLAUDE.md SHALL 只包含规范描述和函数签名，不包含完整实现代码。完整实现示例 SHALL 在 examples/ 目录中提供。

#### Scenario: 创建新工具
- **WHEN** 开发者需要添加新工具
- **THEN** CLAUDE.md SHALL 指导在 tools/ 目录创建 .py 文件，定义 tool() 函数

#### Scenario: 创建新技能
- **WHEN** 开发者需要添加新技能
- **THEN** CLAUDE.md SHALL 指导在 skills/ 目录创建子目录和 SKILL.md 文件

#### Scenario: 查找完整实现示例
- **WHEN** 开发者需要查看 systems/system.py 的完整实现
- **THEN** CLAUDE.md SHALL 引导开发者查看 examples/a-simple-bash-only-workspace/systems/system.py

### Requirement: 编码规范
CLAUDE.md SHALL 包含 Python 编码规范，包括代码风格、命名约定、文档字符串规范。

#### Scenario: 编写符合规范的代码
- **WHEN** AI 助手生成代码
- **THEN** 代码 SHALL 遵循 CLAUDE.md 中定义的编码规范

### Requirement: 运行示例
CLAUDE.md SHALL 包含常用命令示例，展示如何启动各组件。

#### Scenario: 启动 session
- **WHEN** 开发者需要运行 agent
- **THEN** CLAUDE.md SHALL 提供完整的启动命令示例

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