## Why

The current README files have several issues that reduce clarity and usability: the Chinese README uses an uncommon naming convention, there's no cross-linking between language versions, the --base-url note is unnecessarily emphasized, and the "Available Packages" section is mislabeled.

## What Changes

- Rename `README_CN.md` to `README_zh.md` (more common naming convention for Chinese READMEs)
- Add language switch links at the top of both README.md and README_zh.md
- Remove the emphasized note about --base-url (keep it simple in the command example)
- Rename "Available Packages" section to "Available Scripts" (these are CLI commands, not packages)
- Fix license information: change from MIT to AGPLv3 (correct license for this project)
- Ensure consistency between English and Chinese README content

## Capabilities

### Modified Capabilities

- `user-readme`: Update README requirements to include language switching and correct section naming

## Impact

- Renamed file: `README_CN.md` → `README_zh.md`
- Modified files: `README.md`, `README_zh.md`
- No code changes required
