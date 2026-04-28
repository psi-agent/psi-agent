## MODIFIED Requirements

### Requirement: System prompt includes identity statement

The system prompt builder SHALL include an identity statement at the beginning: "You are a personal assistant running inside psi agent."

#### Scenario: Identity statement present
- **WHEN** the system prompt is built
- **THEN** the prompt begins with "You are a personal assistant running inside psi agent."

## ADDED Requirements

### Requirement: Skills section includes rate limit guidance

The system prompt builder SHALL include rate limit guidance in the Skills section to help agents avoid overwhelming external APIs.

#### Scenario: Rate limit guidance present
- **WHEN** the system prompt is built
- **THEN** the Skills section includes guidance about rate limits, preferring fewer larger writes, avoiding tight loops, and respecting 429/Retry-After

### Requirement: Dynamic context files placed after cache boundary

The system prompt builder SHALL place HEARTBEAT.md after the cache boundary marker, separate from stable bootstrap files.

#### Scenario: HEARTBEAT.md in dynamic section
- **WHEN** the system prompt is built
- **THEN** HEARTBEAT.md content appears after the cache boundary marker

#### Scenario: Stable files before cache boundary
- **WHEN** the system prompt is built
- **THEN** AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, BOOTSTRAP.md, and MEMORY.md content appears before the cache boundary marker
