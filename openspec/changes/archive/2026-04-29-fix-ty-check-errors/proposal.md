## Why

The `ty check` command reports errors that are false positives due to ty's limited understanding of complex type patterns used by third-party libraries (tyro) and union types with AsyncGenerator. These errors do not represent actual type safety issues - the code works correctly at runtime. We need to configure ty to suppress these false positives while maintaining type checking for legitimate issues.

## What Changes

- Add `# ty: ignore` comments to suppress false positive errors
- Configure ty to handle third-party library type patterns gracefully
- Document the rationale for each suppression

### Errors to Fix

1. **`src/psi_agent/__main__.py:37`** - `no-matching-overload` error
   - tyro's `cli()` function uses complex overload patterns that ty cannot fully resolve
   - The code is correct; ty just cannot match the Union type to tyro's overloads

2. **`src/psi_agent/session/server.py:140`** - `not-iterable` error
   - `AsyncGenerator[str] | dict[str, Any]` union type is not recognized as async-iterable
   - Runtime check ensures correct handling; ty cannot understand the control flow

## Capabilities

### New Capabilities
- None - this is a configuration/documentation fix

### Modified Capabilities
- None - no behavioral changes

## Impact

- **Type Checking**: ty check will pass without false positives
- **Code Quality**: Suppression comments will document why each ignore is needed
- **Developer Experience**: CI/CD pipeline will not fail on these false positives
