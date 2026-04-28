## 1. Fix a-simple-bash-only-workspace/systems/system.py

- [x] 1.1 Replace `skill_md_path.read_text()` in `_parse_skill_description()` with `await anyio.Path(skill_md_path).read_text()`
- [x] 1.2 Replace `skills_dir.exists()` in `build_system_prompt()` with `await anyio.Path(skills_dir).exists()`
- [x] 1.3 Replace `skills_dir.iterdir()` in `build_system_prompt()` with `async for skill_path in anyio.Path(skills_dir).iterdir()`
- [x] 1.4 Replace `skill_path.is_dir()` in `build_system_prompt()` with `await anyio.Path(skill_path).is_dir()`
- [x] 1.5 Replace `skill_md.exists()` in `build_system_prompt()` with `await anyio.Path(skill_md).exists()`
- [x] 1.6 Add `import anyio` if not already present

## 2. Fix an-openclaw-like-workspace/systems/system.py

- [x] 2.1 Replace `file_path.exists()` in `_read_bootstrap_file()` with `await anyio.Path(file_path).exists()`
- [x] 2.2 Verify `anyio` is already imported (it is present in this file)

## 3. Verification

- [x] 3.1 Run `ruff check` on modified files
- [x] 3.2 Run `ruff format` on modified files
- [x] 3.3 Run `ty check` on modified files
- [x] 3.4 Run `pytest` to verify all tests pass