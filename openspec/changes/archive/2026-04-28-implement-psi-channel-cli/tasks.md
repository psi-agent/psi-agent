## 1. Setup

- [x] 1.1 Create `src/psi_agent/channel/` directory structure
- [x] 1.2 Implement `__init__.py` exports

## 2. Core Implementation

- [x] 2.1 Implement `cli.py` - HTTP client connecting to session socket
- [x] 2.2 Implement request building (OpenAI chat completion format)
- [x] 2.3 Implement non-streaming response handling
- [x] 2.4 Implement streaming response handling
- [x] 2.5 Implement error handling for connection failures

## 3. Integration

- [x] 3.1 Add `psi-channel-cli` entry point to pyproject.toml

## 4. Testing

- [x] 4.1 Create `tests/channel/` directory
- [x] 4.2 Write tests for CLI (request building, response handling)