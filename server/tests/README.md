# Backend Tests

This directory contains the test suite for the Cybermetrics backend API.

## Test Structure

```
tests/
├── __init__.py           # Makes tests a Python package
├── conftest.py          # Shared fixtures and configuration
├── test_example.py      # Example tests demonstrating patterns
├── test_health.py       # Tests for health check endpoint
└── README.md           # This file
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_health.py
```

### Run specific test function
```bash
pytest tests/test_health.py::test_health_endpoint_returns_200
```

### Run tests by marker
```bash
# Run only unit tests
pytest -m unit

# Run only API tests
pytest -m api

# Run only integration tests
pytest -m integration
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=html
```

### Run tests matching a pattern
```bash
pytest -k "health"
```

## Test Markers

Tests are organized using markers defined in `pytest.ini`:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may require external services)
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.auth` - Authentication related tests
- `@pytest.mark.database` - Database related tests
- `@pytest.mark.slow` - Slow running tests

## Writing Tests

### Basic Test Example
```python
import pytest

@pytest.mark.unit
def test_something():
    assert 1 + 1 == 2
```

### Using Fixtures
```python
@pytest.mark.unit
def test_with_fixture(sample_player_data):
    assert sample_player_data["player_id"] == "test123"
```

### Testing API Endpoints
```python
@pytest.mark.api
def test_endpoint(client):
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

### Async Tests
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Available Fixtures

See `conftest.py` for all available fixtures:

- `client` - FastAPI TestClient
- `mock_firebase_credentials` - Mocked Firebase credentials
- `mock_player_repository` - Mocked player repository
- `sample_player_data` - Sample player data
- `mock_auth_token` - Mock authentication token
- `mock_firebase_auth` - Mock Firebase authentication

## Coverage Reports

After running tests with coverage, view the HTML report:
```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# Open the report (Windows)
start htmlcov/index.html
```

## Best Practices

1. **Keep tests isolated** - Each test should be independent
2. **Use descriptive names** - Test names should describe what they test
3. **One assertion per test** - When possible, focus on one thing
4. **Use fixtures** - Reuse common setup code via fixtures
5. **Mark your tests** - Use markers to organize and filter tests
6. **Test edge cases** - Don't just test the happy path
7. **Mock external dependencies** - Use mocks for Firebase, databases, etc.

## Continuous Integration

Tests are automatically run in the CI pipeline on every push and pull request to `main` and `develop` branches.
