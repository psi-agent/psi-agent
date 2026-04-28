## Context

CONTRIBUTING.md is a documentation file that sets contribution guidelines for the project. Currently it mandates Claude Code as the only acceptable coding agent for PR contributions. The actual intent is to ensure code quality through automated coding agents while allowing flexibility in tool choice.

The file currently has Chinese content first, followed by English content. The standard convention for open-source projects is to have English as the primary language.

## Goals / Non-Goals

**Goals:**
- Update CONTRIBUTING.md to allow any coding agent (not just Claude Code)
- Require that alternative agents have OpenSpec installed and understand CLAUDE.md
- Restructure document with English first, then Chinese
- Ensure both language versions are consistent

**Non-Goals:**
- Changing the underlying code quality requirements
- Modifying any code or configuration files
- Creating new tooling or infrastructure

## Decisions

### Document Structure
- **Decision**: English section first, then Chinese section
- **Rationale**: English is the lingua franca of open source; this makes the document more accessible to international contributors

### Coding Agent Requirements
- **Decision**: Allow any coding agent with proper setup
- **Rationale**: The goal is code quality through automation, not tool lock-in. Contributors should have flexibility while maintaining standards.
- **Requirements for alternative agents**:
  1. OpenSpec must be installed (for change management workflow)
  2. Agent must be configured to read and understand CLAUDE.md content

### Language Consistency
- **Decision**: Both versions must convey identical requirements
- **Rationale**: Avoids confusion where contributors follow different rules based on which language they read

## Risks / Trade-offs

- **Risk**: Contributors may not properly configure alternative agents → Mitigation: Clear setup instructions in CONTRIBUTING.md
- **Risk**: Different agents may interpret CLAUDE.md differently → Mitigation: Acceptable trade-off for flexibility; code review catches issues
