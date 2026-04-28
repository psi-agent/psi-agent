## Context

psi-agent 项目已完成基础实现，需要完善项目配置。当前状态：
- 软件协议为 MIT（临时设置）
- 作者信息缺少邮箱
- 版本号硬编码在 pyproject.toml
- CLAUDE.md 缺少具体代码风格规范（import顺序、async规范、docstring格式等）

## Goals / Non-Goals

**Goals:**
- 将软件协议改为 AGPL v3（适合开源 AI agent 项目）
- 添加作者邮箱 hzhangxyz@outlook.com
- 使用 hatch-vcs 从 git tag 动态获取版本
- 固化现有代码风格到 CLAUDE.md（import顺序、async上下文管理器规范、错误处理模式、docstring格式）

**Non-Goals:**
- 不修改任何代码逻辑
- 不添加新功能
- 不改变项目结构

## Decisions

### 软件协议选择

使用 **AGPL v3**。

理由：
- AGPL v3 要求网络服务使用者也能获得源代码
- 适合 AI agent 这类可能作为服务部署的项目
- 保护开源生态

替代方案：
- MIT：过于宽松，不利于保护开源成果
- GPL v3：不覆盖网络服务场景

### 版本管理方案

使用 **hatch-vcs**。

理由：
- 从 git tag 自动生成版本号
- 避免手动维护版本号不一致
- hatchling 原生支持

替代方案：
- 硬编码版本：需要手动同步 git tag 和 pyproject.toml
- setuptools_scm：需要额外配置，不如 hatch-vcs 简洁

### 代码风格固化

从现有代码提取规范：
- import顺序：stdlib → third-party → local（符合 ruff isort）
- async上下文管理器：使用 `__aenter__`/`__aexit__`，`_client` 设为 `None` 后关闭
- 错误处理：try-except + loguru记录 + 返回错误dict（含status_code）
- 类型注解：使用 `| None` 语法（Python 3.14+）

### 文档字符串格式

使用 **Google style docstring**。

理由：
- 现有代码已使用此风格
- 格式清晰易读
- 与 Sphinx 兼容
- 参数和返回值描述直观

格式规范：
```python
def function(arg1: str, arg2: int) -> bool:
    """简短描述（一行）。

    详细描述（可选，多行）。

    Args:
        arg1: 第一个参数的描述。
        arg2: 第二个参数的描述。

    Returns:
        返回值的描述。

    Raises:
        ValueError: 可能抛出的异常描述。
    """
```

替代方案：
- NumPy style：格式较冗长
- reST style：Sphinx 默认但不直观

## Risks / Trade-offs

- hatch-vcs 在没有 tag 时会生成 `0.0.0` 版本 → 适合当前开发阶段，发版时再打 tag
- AGPL v3 限制商业使用 → 适合本项目开源定位