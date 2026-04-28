## MODIFIED Requirements

### Requirement: README.md contains essential sections
The README.md SHALL include the following sections:
1. Project title and brief description
2. Language switch link (to README_zh.md)
3. Installation instructions
4. Quick start example
5. Component overview
6. Available scripts list
7. Link to detailed documentation

#### Scenario: User reads README.md structure
- **WHEN** a user reads README.md
- **THEN** they can quickly understand what psi-agent is, how to install it, and how to get started
- **AND** they can switch to the Chinese version via the language link

## ADDED Requirements

### Requirement: Chinese README uses common naming convention
The Chinese README SHALL be named `README_zh.md` following common conventions.

#### Scenario: User accesses Chinese README
- **WHEN** a user wants to read the Chinese documentation
- **THEN** they can find it at `README_zh.md`

### Requirement: Language switch links are provided
Both README.md and README_zh.md SHALL provide language switch links at the top of the file.

#### Scenario: User switches language
- **WHEN** a user is reading README.md
- **THEN** they see a link to README_zh.md at the top
- **WHEN** a user is reading README_zh.md
- **THEN** they see a link to README.md at the top
