## Context

当前代码库使用 `pathlib.Path` 和 `anyio.Path` 混合模式：
- IO 操作使用 `anyio.Path` (正确)
- 类型注解使用 `pathlib.Path`
- 数据类字段使用 `pathlib.Path`
- 路径操作使用 `pathlib.Path`

用户希望统一使用 `anyio.Path`，实现完全一致的代码风格。

### anyio.Path 特性

`anyio.Path` 是 `pathlib.Path` 的异步封装，支持：
- 所有路径操作：`.parent`, `.name`, `.suffix`, `/` 操作符
- 所有 IO 操作（异步）：`.exists()`, `.read_text()`, `.iterdir()` 等
- 类型注解：可以作为类型使用

## Goals / Non-Goals

**Goals:**
- 完全移除 `pathlib.Path` 的 import
- 所有路径相关代码统一使用 `anyio.Path`
- 类型注解使用 `anyio.Path`
- 数据类字段使用 `anyio.Path`
- 保持所有测试通过

**Non-Goals:**
- 修改外部 API 行为
- 修改测试逻辑

## Decisions

### Decision 1: 使用 `anyio.Path` 作为唯一的路径类型

**Rationale:** 统一代码风格，避免混用两种 Path 类型。`anyio.Path` 支持所有 `pathlib.Path` 的操作，包括非 IO 操作。

**实现方式:**
```python
# 之前
from pathlib import Path
def foo(path: Path) -> Path:
    return path.parent / "child"

# 之后
import anyio
def foo(path: anyio.Path) -> anyio.Path:
    return path.parent / "child"
```

### Decision 2: 数据类字段类型改为 `anyio.Path`

**Rationale:** 保持类型一致性。`anyio.Path` 对象可以直接存储在数据类中。

**实现方式:**
```python
# 之前
@dataclass
class Schedule:
    task_dir: Path

# 之后
@dataclass
class Schedule:
    task_dir: anyio.Path
```

### Decision 3: Config 类返回 `anyio.Path`

**Rationale:** Config 类的属性方法返回路径对象，应使用统一类型。

**实现方式:**
```python
# 之前
@property
def socket_path(self) -> Path:
    return Path(self.session_socket)

# 之后
@property
def socket_path(self) -> anyio.Path:
    return anyio.Path(self.session_socket)
```

## Risks / Trade-offs

### Risk: 类型检查器兼容性
**Mitigation:** `anyio.Path` 是 `pathlib.Path` 的子类，类型检查应该兼容。运行 `ty check` 验证。

### Risk: 第三方库兼容性
**Mitigation:** 检查所有使用 Path 的地方，确保 `anyio.Path` 可以正常工作。大多数接受 `Path` 的地方也接受 `anyio.Path`。

### Risk: 性能影响
**Mitigation:** `anyio.Path` 的非 IO 操作（如 `.parent`, `.name`）是同步的，性能影响可忽略。
