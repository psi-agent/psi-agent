## 1. Implementation

- [x] 1.1 Define `KNOWN_SDK_PARAMS` set in `client.py` containing standard OpenAI API parameters
- [x] 1.2 Add `_split_params()` method to separate request body into SDK params and extra params
- [x] 1.3 Modify `_non_stream_request()` to use `extra_body` for provider-specific parameters
- [x] 1.4 Modify `_stream_request()` to use `extra_body` for provider-specific parameters

## 2. Testing

- [x] 2.1 Add unit test for `_split_params()` method
- [x] 2.2 Add unit test for request with `thinking` parameter
- [x] 2.3 Add unit test for request with `reasoning_effort` parameter
- [x] 2.4 Add unit test for request with both provider parameters
- [x] 2.5 Add unit test verifying backward compatibility (no provider params)

## 3. Verification

- [x] 3.1 Run `ruff check` and `ruff format`
- [x] 3.2 Run `ty check` for type checking
- [x] 3.3 Run `pytest` to ensure all tests pass
