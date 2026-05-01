## ADDED Requirements

### Requirement: AI module has comprehensive documentation
The AI module SHALL have a CLAUDE.md file at `src/psi_agent/ai/CLAUDE.md` documenting the overall architecture, design philosophy, and component relationships.

#### Scenario: Developer reads AI module documentation
- **WHEN** a developer opens `src/psi_agent/ai/CLAUDE.md`
- **THEN** they SHALL find documentation describing the unified OpenAI chat completions interface, the two adapter components, and how they relate to each other

### Requirement: OpenAI completions adapter has dedicated documentation
The openai-completions adapter SHALL have a CLAUDE.md file at `src/psi_agent/ai/openai_completions/CLAUDE.md` documenting its design, implementation details, and interface.

#### Scenario: Developer reads OpenAI adapter documentation
- **WHEN** a developer opens `src/psi_agent/ai/openai_completions/CLAUDE.md`
- **THEN** they SHALL find documentation describing the direct forwarding approach, configuration parameters, error handling patterns, and provider-specific parameter support

### Requirement: Anthropic messages adapter has dedicated documentation
The anthropic-messages adapter SHALL have a CLAUDE.md file at `src/psi_agent/ai/anthropic_messages/CLAUDE.md` documenting its design, protocol translation logic, and interface.

#### Scenario: Developer reads Anthropic adapter documentation
- **WHEN** a developer opens `src/psi_agent/ai/anthropic_messages/CLAUDE.md`
- **THEN** they SHALL find documentation describing the OpenAI-to-Anthropic protocol translation, the translator component, streaming handling, and tool call conversion

### Requirement: Documentation follows consistent structure
All three CLAUDE.md files SHALL follow a consistent structure including: module overview, core components, interface definitions, design decisions, and relationships with other modules.

#### Scenario: Documentation structure consistency
- **WHEN** comparing the three CLAUDE.md files
- **THEN** each SHALL contain sections for overview, components, interfaces, design decisions, and module relationships in a similar order

### Requirement: Documentation records design patterns
The documentation SHALL explicitly record the shared design patterns across adapters including: async context manager pattern, unified error handling format, and consistent logging granularity.

#### Scenario: Design patterns documented
- **WHEN** a developer reads any adapter CLAUDE.md
- **THEN** they SHALL find documentation of the async context manager pattern, the `{error, status_code}` error return format, and DEBUG/INFO logging level usage