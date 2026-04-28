## 1. 更新 pyproject.toml 版本号

- [x] 1.1 更新 aiohttp: >=3.9.0 → >=3.13.5
- [x] 1.2 更新 anyio: >=4.0.0 → >=4.13.0
- [x] 1.3 更新 loguru: >=0.7.0 → >=0.7.3
- [x] 1.4 更新 tyro: >=0.8.0 → >=1.0.13
- [x] 1.5 更新 pytest: >=8.0.0 → >=9.0.3
- [x] 1.6 更新 pytest-asyncio: >=0.23.0 → >=1.3.0
- [x] 1.7 更新 ruff: >=0.4.0 → >=0.15.12
- [x] 1.8 更新 ty: >=0.0.0 → >=0.0.33

## 2. 同步依赖锁文件

- [x] 2.1 运行 `uv sync` 更新 uv.lock

## 3. 运行质量检查

- [x] 3.1 运行 `ruff check` 确保 lint 通过
- [x] 3.2 运行 `ruff format` 确保格式正确
- [x] 3.3 运行 `ty check` 确保类型检查通过（源代码通过，tests pytest 是 dev 依赖）
- [x] 3.4 运行 `uv run psi-ai-openai-completions --help` 验证 CLI 正常（tyro 1.0 API 兼容）