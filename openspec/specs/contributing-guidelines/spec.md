### Requirement: Coding agent requirement
All PR code MUST be written by a coding agent (not manually by humans).

#### Scenario: PR with coding agent code
- **WHEN** a contributor submits a PR with code written by a coding agent
- **THEN** the PR is eligible for review

#### Scenario: PR with manually written code
- **WHEN** a contributor submits a PR with manually written code
- **THEN** the PR is not accepted

### Requirement: Coding agent flexibility
Contributors MAY use any coding agent that meets the setup requirements.

#### Scenario: Using Claude Code
- **WHEN** a contributor uses Claude Code
- **THEN** no additional setup is required as Claude Code natively reads CLAUDE.md

#### Scenario: Using alternative coding agent
- **WHEN** a contributor uses an alternative coding agent
- **THEN** the agent must have OpenSpec installed and be configured to understand CLAUDE.md content

### Requirement: Document structure
CONTRIBUTING.md MUST present English content first, followed by Chinese content.

#### Scenario: Reading English section
- **WHEN** a contributor opens CONTRIBUTING.md
- **THEN** the English section appears at the top of the file

#### Scenario: Reading Chinese section
- **WHEN** a contributor scrolls past the English section
- **THEN** the Chinese section follows with identical requirements

### Requirement: Language consistency
English and Chinese versions MUST convey identical requirements and information.

#### Scenario: Comparing language versions
- **WHEN** comparing English and Chinese sections
- **THEN** both sections describe the same requirements and guidelines
