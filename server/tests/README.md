# Test Suite Documentation

This directory contains comprehensive unit tests for the Cybermetrics backend application.

## Test Structure

Tests are organized by module, with each module having its own `tests/` subdirectory:

```
server/
├── domain/
│   └── tests/
│       ├── test_auth_domain.py
│       ├── test_player_domain.py
│       ├── test_saved_players_domain.py
│       └── test_roster_domain.py
├── services/
│   └── tests/
│       ├── test_auth_service.py
│       ├── test_player_search_service.py
│       ├── test_saved_players_service.py
│       └── test_roster_avg_service.py
├── models/
│   └── tests/
│       ├── test_auth_models.py
│       └── test_player_models.py
├── middleware/
│   └── tests/
│       ├── test_auth_middleware.py
│       ├── test_error_handler.py
│       └── test_rate_limit.py
├── conftest.py          # Shared fixtures
└── pytest.ini           # Pytest configuration
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=. --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Files

```bash
# Run domain tests
pytest domain/tests/

# Run service tests
pytest services/tests/

# Run a specific test file
pytest domain/tests/test_auth_domain.py

# Run a specific test class
pytest domain/tests/test_auth_domain.py::TestAuthDomain

# Run a specific test method
pytest domain/tests/test_auth_domain.py::TestAuthDomain::test_validate_signup_data_valid
```

### Run Tests by Marker

```bash
# Run only async tests
pytest -m asyncio

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Stop on First Failure

```bash
pytest -x
```

## Test Coverage

The test suite aims for high coverage across:

- **Domain Layer**: Business logic validation
- **Service Layer**: Service orchestration and integration
- **Models**: Pydantic model validation
- **Middleware**: Authentication, error handling, and rate limiting

### Coverage Goals

- Domain layer: 95%+
- Service layer: 90%+
- Models: 100%
- Middleware: 90%+

## Writing New Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_is_being_tested>`

### Example Test Structure

```python
import pytest
from module import ClassToTest

class TestClassName:
    """Unit tests for ClassName"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.instance = ClassToTest()
    
    def test_method_success(self):
        """Test successful execution"""
        result = self.instance.method()
        assert result == expected_value
    
    def test_method_failure(self):
        """Test failure case"""
        with pytest.raises(Exception):
            self.instance.method(invalid_input)
    
    @pytest.mark.asyncio
    async def test_async_method(self):
        """Test async method"""
        result = await self.instance.async_method()
        assert result is not None
```

### Using Fixtures

Shared fixtures are defined in `conftest.py`:

```python
def test_with_fixture(sample_user_data):
    """Test using shared fixture"""
    assert sample_user_data["email"] == "test@example.com"
```

### Mocking Dependencies

Use `unittest.mock` for mocking:

```python
from unittest.mock import Mock, AsyncMock

def test_with_mock():
    mock_repo = Mock()
    mock_repo.get_data = AsyncMock(return_value={"data": "value"})
    
    service = Service(mock_repo)
    result = await service.process()
    
    mock_repo.get_data.assert_called_once()
```

## Test Categories

### Unit Tests

Test individual components in isolation with mocked dependencies.

```python
@pytest.mark.unit
def test_unit():
    pass
```

### Integration Tests

Test multiple components working together (not yet implemented).

```python
@pytest.mark.integration
def test_integration():
    pass
```

### Async Tests

Tests for async functions must be marked with `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## Continuous Integration

Tests are automatically run in CI/CD pipelines on:
- Pull requests
- Merges to main branch
- Release tags

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:
1. You're in the server directory
2. Python path includes the server directory
3. All `__init__.py` files exist

### Async Test Failures

Ensure async tests are marked with `@pytest.mark.asyncio` and pytest-asyncio is installed.

### Coverage Not Working

Ensure pytest-cov is installed:
```bash
pip install pytest-cov
```

## Best Practices

1. **Test One Thing**: Each test should verify one specific behavior
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests with setup, execution, and verification
4. **Mock External Dependencies**: Don't make real API calls or database queries
5. **Use Fixtures**: Share common setup code via fixtures
6. **Test Edge Cases**: Include tests for error conditions and boundary cases
7. **Keep Tests Fast**: Unit tests should run in milliseconds
8. **Maintain Independence**: Tests should not depend on each other

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Pydantic Testing](https://docs.pydantic.dev/latest/concepts/testing/)
