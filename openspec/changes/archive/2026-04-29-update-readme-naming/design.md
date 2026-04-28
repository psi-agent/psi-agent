## Context

The README files were recently created but have several naming and content issues that need correction. This is a documentation-only change to improve clarity and follow common conventions.

## Goals / Non-Goals

**Goals:**
- Use `README_zh.md` naming (common convention for Chinese READMEs)
- Add language switch links for easy navigation between English and Chinese versions
- Simplify the --base-url documentation (remove emphasized note)
- Correct section naming from "Available Packages" to "Available Scripts"

**Non-Goals:**
- Changing any actual content or functionality descriptions
- Adding new sections or documentation

## Decisions

1. **README_zh.md naming**
   - Rationale: `README_zh.md` is the more common convention (e.g., Vue, Element Plus use this pattern)
   - Alternative considered: `README_CN.md` - less common, `README.zh-CN.md` - also valid but `_zh` is simpler

2. **Language switch at top of file**
   - Rationale: Users should immediately see the option to switch languages
   - Format: `[中文](README_zh.md) | [English](README.md)`

3. **Remove emphasized --base-url note**
   - Rationale: The example already shows `--base-url` with a comment, no need for an additional emphasized note

## Risks / Trade-offs

- **Risk**: Existing links to `README_CN.md` will break
  - Mitigation: This is a new file with no external links yet
