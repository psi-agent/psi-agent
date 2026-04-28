## Context

psi-agent is a portable and componentized agent framework. Currently, the project uses `CLAUDE.md` as its readme (referenced in `pyproject.toml`), which is developer-focused documentation for AI assistants. Users visiting the GitHub repository or PyPI package page need a clear, simple introduction to understand and use the framework.

## Goals / Non-Goals

**Goals:**
- Provide a user-friendly README.md that introduces the project
- Include installation instructions via pip/uv
- Show a quick start example
- Give an overview of the component architecture
- Link to CLAUDE.md for detailed documentation

**Non-Goals:**
- Comprehensive API documentation (that belongs in docs/)
- Detailed implementation guides (covered in CLAUDE.md)
- Changing any code or functionality

## Decisions

1. **README.md Structure**
   - Rationale: Follow standard Python project README conventions
   - Sections: Title/Badge, Introduction, Installation, Quick Start, Components, Documentation Link

2. **Keep CLAUDE.md Separate**
   - Rationale: CLAUDE.md serves a different audience (AI assistants/developers) and should remain unchanged
   - The new README.md targets end users who want to quickly understand and use the framework

3. **Update pyproject.toml readme field**
   - Rationale: PyPI will display README.md on the package page, which is more appropriate for users than CLAUDE.md

## Risks / Trade-offs

- **Risk**: README.md may become out of sync with CLAUDE.md
  - Mitigation: Keep README.md concise and link to CLAUDE.md for details
- **Trade-off**: Two documentation files to maintain
  - Acceptable: They serve different purposes and audiences
