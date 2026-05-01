## Context

psi-agent 是一个以可移植性和组件化为核心理念的 agent 框架，包含 57 个 Python 文件分布在多个组件中：
- `psi_ai_*`: LLM 提供商适配器
- `psi_session`: Agent 运行循环
- `psi_channel_*`: 消息通道适配器
- `psi_workspace_*`: Workspace 管理器

CLAUDE.md 定义了详细的编码规范，但代码库在演进过程中可能存在偏离规范的情况。本次审计将系统性检查所有文件。

## Goals / Non-Goals

**Goals:**
- 识别所有偏离 CLAUDE.md 规范的代码
- 分类违规类型（类型注解、import 顺序、async 模式等）
- 提供具体的修复建议
- 确保代码库达到一致的规范遵循度

**Non-Goals:**
- 不修改任何功能代码（仅审计和报告）
- 不添加新功能
- 不改变 API 行为

## Decisions

### 1. 审计范围

检查 CLAUDE.md 中定义的所有规范：
- `from __future__ import annotations` 开头
- Python 3.14+ 现代语法（`X | Y`, `list[X]`, `dict[K, V]`）
- Import 顺序（stdlib → third-party → local）
- Google-style docstrings
- Async 上下文管理器模式
- 错误处理规范
- 防御性编程（null 检查）
- CLI 安全规范（敏感参数掩码）

### 2. 审计方法

逐文件检查，记录每个违规点：
- 文件路径
- 行号
- 违规类型
- 具体描述
- 修复建议

### 3. 分类标准

违规分为三个严重级别：
- **Critical**: 必须修复（如缺少 `from __future__ import annotations`）
- **Warning**: 应该修复（如 import 顺序不正确）
- **Info**: 建议修复（如 docstring 格式不完整）

## Risks / Trade-offs

- **风险**: 审计可能遗漏某些边缘情况 → 通过逐文件完整阅读来最小化此风险
- **权衡**: 完整审计耗时较长 → 确保审计质量优先于速度