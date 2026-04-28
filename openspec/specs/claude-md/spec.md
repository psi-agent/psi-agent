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

#### Scenario: 创建新工具
- **WHEN** 开发者需要添加新工具
- **THEN** CLAUDE.md SHALL 指导在 tools/ 目录创建 .py 文件，定义 tool() 函数

#### Scenario: 创建新技能
- **WHEN** 开发者需要添加新技能
- **THEN** CLAUDE.md SHALL 指导在 skills/ 目录创建子目录和 SKILL.md 文件

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