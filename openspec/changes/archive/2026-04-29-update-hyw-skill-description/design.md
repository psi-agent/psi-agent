## Context

The hyw skill is a simple skill in the example workspace that adds a contemplative prefix "何意味？" (He Yi Wei - "What does it mean?") to user-facing questions. Currently, the skill description is too subtle about when it should be used, and it hints at the key phrase in the description itself.

The skill is located at `examples/a-simple-bash-only-workspace/skills/hyw/SKILL.md` and follows the standard skill format with YAML frontmatter.

## Goals / Non-Goals

**Goals:**
- Update the skill description to make it unambiguous that this skill is mandatory for all user questioning scenarios
- Remove the phrase "何意味" from the description so LLMs only discover it when reading the full skill content
- Maintain the existing skill behavior and instructions

**Non-Goals:**
- Changing the actual behavior of the skill (the prefix behavior remains the same)
- Modifying any other skills or components
- Adding new functionality

## Decisions

### Description wording
The description should:
1. Use clear, directive language like "MUST" or "required" to indicate mandatory usage
2. Specify the trigger condition: "when asking the user any question"
3. Not reveal the specific phrase or behavior - that should only be discoverable in the skill body

Proposed new description:
> "Mandatory skill for all user-facing questions. MUST be used whenever asking the user any question."

This makes the requirement explicit without revealing the implementation.

## Risks / Trade-offs

**Risk**: Overly strict description may cause the LLM to apply the skill inappropriately (e.g., to rhetorical questions)
→ **Mitigation**: The skill body already has explicit instructions about when NOT to apply (rhetorical questions, internal reasoning)

**Trade-off**: The new description is more prescriptive, which reduces ambiguity but may feel less "philosophical" in tone
→ This is acceptable because clarity of when to use the skill is more important than stylistic consistency
