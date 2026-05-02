## Why

Channel 组件（cli、repl、telegram）在代码结构、日志粒度、错误处理、设计思路等方面存在不一致性，影响代码可维护性和开发效率。三个子模块由不同时间、不同开发方式构建，导致风格差异。现在进行统一审查和重构，以提高代码一致性和可维护性。

## What Changes

### 1. 日志粒度不一致

- **cli.py**: DEBUG 级别记录完整请求体、响应体、每个流式 chunk
- **repl/client.py**: DEBUG 级别记录完整请求体、响应体、每个流式 chunk（与 cli 一致）
- **telegram/client.py**: DEBUG 级别记录完整请求体、响应体、每个流式 chunk（与 repl 一致）
- **问题**: `cli.py` 缺少 INFO 级别的请求接收日志，而 `repl/cli.py` 和 `telegram/cli.py` 都有 `logger.info("Starting psi-channel-xxx")`

### 2. 设计思路不一致

- **cli.py**: 独立实现，不使用 Client 类，直接在 `send_message()` 函数中处理请求
- **repl/**: 分离为 `Repl`（界面）、`ReplClient`（HTTP 客户端）、`ReplConfig`（配置）三个类
- **telegram/**: 分离为 `TelegramBot`（业务逻辑）、`TelegramClient`（HTTP 客户端）、`TelegramConfig`（配置）三个类
- **问题**: cli.py 没有遵循 repl/telegram 的三层分离模式，缺少 Client 类抽象

### 3. 请求体构建不一致

- **cli.py**: 请求体包含 `"model": "session"` 字段
- **repl/client.py**: 请求体不包含 `"model"` 字段
- **telegram/client.py**: 请求体包含 `"model": "session"` 和 `"user": user_id` 字段
- **问题**: model 字段是否应该存在？user 字段在 telegram 中添加但 repl 中没有（设计意图是否正确？）

### 4. 错误处理返回格式不一致

- **cli.py**: 返回 `f"Error: {text}"` 格式
- **repl/client.py**: 返回 `f"Error: Session returned status {response.status}"` 格式
- **telegram/client.py**: 返回 `f"Error: Session returned status {response.status}"` 格式
- **问题**: cli.py 的错误格式与其他两个不一致

### 5. Async 上下文管理器规范不一致

- **repl/client.py**: `__aexit__` 中清理 `_connector` 但不记录日志
- **telegram/client.py**: `__aexit__` 中清理 `_connector` 但不记录日志
- **问题**: 两个 Client 类的 `__aexit__` 都没有记录 connector 关闭日志（与 session 关闭日志不对称）

### 6. 流式处理中 content 检查不一致

- **cli.py**: `if content is not None:` 检查后 append，然后 `if content:` 才打印和记录
- **repl/client.py**: `if content:` 检查后同时 append、记录、调用 callback
- **telegram/client.py**: `if content:` 检查后同时 append、记录、调用 callback
- **问题**: cli.py 使用 `is not None` 检查，repl/telegram 使用 truthy 检查。空字符串处理方式不同

### 7. CLI 类命名不一致

- **cli/cli.py**: 类名为 `Cli`
- **repl/cli.py**: 类名为 `Repl`
- **telegram/cli.py**: 类名为 `Telegram`
- **问题**: `Cli` 命名过于通用，与其他两个模块的命名风格不一致

### 8. 配置类设计不一致

- **repl/config.py**: 有 `socket_path()` 和 `get_history_path()` 两个方法
- **telegram/config.py**: 只有 `socket_path()` 方法
- **问题**: 方法命名风格一致，但 telegram 缺少额外方法（这是合理的差异）

### 9. 模块导出不一致

- **repl/__init__.py**: 导出 `Repl`, `ReplClient`, `ReplConfig`
- **telegram/__init__.py**: 导出空列表 `__all__ = []`
- **问题**: telegram 模块不导出任何公共接口，与 repl 模块不一致

### 10. 文档字符串风格不一致

- **cli.py**: 使用简短描述，Args/Returns 分段
- **repl/client.py**: 使用简短描述，Args/Returns/Raises 分段
- **telegram/client.py**: 使用简短描述，Args/Returns/Raises 分段
- **问题**: cli.py 缺少 Raises 段（虽然函数可能抛出异常）

## Capabilities

### New Capabilities

- `channel-consistency`: Channel 组件代码一致性规范，包括日志粒度、设计模式、错误处理、命名风格等

### Modified Capabilities

- `channel-cli`: CLI channel 需要重构以遵循三层分离模式
- `repl-channel`: REPL channel 需要调整日志和错误处理细节
- `telegram-channel`: Telegram channel 需要调整模块导出和日志细节

## Impact

- `src/psi_agent/channel/cli/cli.py` - 需要重构，添加 Client 类
- `src/psi_agent/channel/cli/` - 可能需要新增 config.py 和 client.py
- `src/psi_agent/channel/repl/client.py` - 调整日志和错误处理
- `src/psi_agent/channel/telegram/__init__.py` - 调整模块导出
- `src/psi_agent/channel/telegram/client.py` - 调整日志细节