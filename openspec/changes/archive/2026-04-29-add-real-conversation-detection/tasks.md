## 1. Add Real Conversation Detection Functions

- [x] 1.1 Add `has_meaningful_conversation_content()` function to detect if a message contains meaningful dialogue content
- [x] 1.2 Add `is_real_conversation_message()` function to determine if a message is part of real conversation
- [x] 1.3 Add `_contains_real_conversation_messages()` helper function to check if history has any real conversation

## 2. Integrate into compact_history

- [x] 2.1 Modify `compact_history()` to check for real conversation before compaction
- [x] 2.2 Add early return when no real conversation messages exist

## 3. Update Documentation

- [x] 3.1 Update DIFF.md to document the new real conversation detection feature

## 4. Code Quality

- [x] 4.1 Run `ruff check` and fix any lint errors
- [x] 4.2 Run `ruff format` to ensure proper formatting
- [x] 4.3 Run `ty check` to verify type annotations
