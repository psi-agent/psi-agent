## 1. Fix

- [x] 1.1 Move system prompt loading to `__aenter__` in runner.py
- [x] 1.2 Remove `_get_cached_system_prompt` method or make it sync
- [x] 1.3 Update `_build_messages` to use the cached value directly