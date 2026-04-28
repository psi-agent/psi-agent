## Why

代码库中还有一些被忽略的 lint 和 typing 错误需要处理：

1. **tyro 库类型问题** - `tyro.cli()` 不接受 Union 类型，这是 tyro 库的限制，需要向 tyro 提交 issue/PR
2. **python-telegram-bot 类型问题** - `updater` 属性类型注解问题，可以通过添加 `assert` 解决
3. **examples 中的 E501 忽略** - 行过长警告，可以拆分长行
4. **tests 中的 E402 忽略** - import 位置问题，可以移动到文件顶部

## What Changes

- 为 tyro 库创建最小复现示例，用于提交 issue
- 在 `telegram/bot.py` 中添加 `assert` 来帮助类型检查器
- 修复 `examples/.../system.py` 中的 E501 违规（拆分长行）
- 修复 `tests/.../test_cron.py` 中的 E402 违规（移动 import）

## Capabilities

### New Capabilities

无

### Modified Capabilities

- `telegram-channel`: 添加 assert 语句以消除 ty ignore 注释
- `type-safety-improvements`: 扩展以覆盖更多忽略情况

## Impact

- `src/psi_agent/channel/telegram/bot.py`: 添加 assert 语句
- `examples/an-openclaw-like-workspace/systems/system.py`: 拆分长行
- `tests/session/schedule/test_cron.py`: 移动 import 到顶部
- 创建 tyro issue 复现示例（外部）
