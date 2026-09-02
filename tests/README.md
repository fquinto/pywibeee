# Tests

Test suite for the pywibeee library (`src/pywibeee`).

Install the library with its test dependencies and run pytest:

```sh
pip install -e ".[test]"
pytest
```

## Test breakdown

| File | Coverage |
|------|----------|
| `test_client.py` | `WibeeeAPI` client: XML parsing, HTTP errors, retries, discovery deadline, push server configuration, device actions, diagnostics |

The Home Assistant integration built on this library lives in
`home-assistant/core` and is tested there (`tests/components/wibeee`).
