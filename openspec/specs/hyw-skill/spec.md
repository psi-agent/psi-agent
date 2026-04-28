## Requirements

### Requirement: Skill description enforces mandatory usage
The skill description in the YAML frontmatter SHALL clearly state that this skill is mandatory for all user-facing questions. The description SHALL NOT contain the phrase "何意味" or any hint of the specific behavior.

#### Scenario: LLM reads skill list
- **WHEN** the LLM reads the list of available skills with their descriptions
- **THEN** the LLM SHALL understand that the hyw skill MUST be used for any user-facing question
- **AND** the LLM SHALL NOT know the specific phrase "何意味" from the description alone

#### Scenario: LLM reads full skill content
- **WHEN** the LLM decides to read the full skill content after seeing the description
- **THEN** the LLM SHALL discover the specific behavior (adding "何意味？" prefix) in the skill body
