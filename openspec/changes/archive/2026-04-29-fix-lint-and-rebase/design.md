## Context

The dev/coverage branch has linting issues that will fail CI. The issues are:
- E501: Line too long in tests/session/test_runner.py and tests/session/test_server.py
- F401: Unused import (AsyncMock) in tests/workspace/test_snapshot.py
- I001: Unsorted imports in tests/workspace/test_snapshot.py

## Goals / Non-Goals

**Goals:**
- Fix all linting errors to pass CI
- Rebase branch onto origin/main

**Non-Goals:**
- Changing test behavior
- Adding new tests

## Decisions

### 1. Line Length Fixes
Break long lines to stay within 100 character limit using multi-line format.

### 2. Import Fixes
- Remove unused AsyncMock import from test_snapshot.py
- Sort imports according to ruff isort rules

## Risks / Trade-offs

- Minimal risk - only formatting changes to test files
