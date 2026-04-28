## Why

CLAUDE.md 中 systems/system.py 的示例代码过于冗长（约 80 行），这些代码可以在 `examples/` 目录中找到完整实现。CLAUDE.md 应该只包含规范描述，而不是完整的实现代码。

## What Changes

- 精简 systems/ 目录的示例代码，只保留规范描述和简短示例
- 移除完整的 `build_system_prompt()` 和 `compact_history()` 实现
- 保留函数签名和行为描述，移除详细代码

## Capabilities

### New Capabilities

None - 这是文档精简，不引入新能力。

### Modified Capabilities

- `claude-md`: 精简 systems/system.py 示例代码

## Impact

- **CLAUDE.md**: systems/ 目录部分从约 80 行精简到约 20 行
- **开发者体验**: 更清晰的规范描述，详细实现参考 examples/
