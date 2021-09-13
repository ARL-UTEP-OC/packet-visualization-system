import pytest
from components.mock_component import NumberAddition


def test_add_numbers():
    assert NumberAddition.add_numbers(3, 4) is 7
