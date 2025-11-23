"""
Example test file demonstrating different types of tests.
This file can be used as a template for creating new tests.
"""
import pytest


@pytest.mark.unit
def test_example_basic():
    """Example of a basic unit test."""
    assert 1 + 1 == 2


@pytest.mark.unit
def test_example_with_fixture(sample_player_data):
    """Example test using a fixture from conftest.py."""
    assert sample_player_data["player_id"] == "test123"
    assert sample_player_data["name"] == "Test Player"


@pytest.mark.unit
def test_example_string_operations():
    """Example test for string operations."""
    test_string = "Cybermetrics"
    assert test_string.lower() == "cybermetrics"
    assert len(test_string) == 12
    assert test_string.startswith("Cyber")


@pytest.mark.unit
def test_example_list_operations():
    """Example test for list operations."""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert 3 in test_list
    assert test_list[0] == 1
    assert test_list[-1] == 5


@pytest.mark.unit
def test_example_dict_operations():
    """Example test for dictionary operations."""
    test_dict = {"name": "Test", "value": 42}
    assert "name" in test_dict
    assert test_dict["value"] == 42
    assert len(test_dict) == 2


@pytest.mark.unit
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25),
])
def test_example_parametrized(input, expected):
    """Example of a parametrized test."""
    assert input ** 2 == expected


class TestExampleClass:
    """Example test class for grouping related tests."""
    
    @pytest.mark.unit
    def test_class_method_1(self):
        """First test in the class."""
        assert True
    
    @pytest.mark.unit
    def test_class_method_2(self):
        """Second test in the class."""
        result = [x * 2 for x in range(5)]
        assert result == [0, 2, 4, 6, 8]
