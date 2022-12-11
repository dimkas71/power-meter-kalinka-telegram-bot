import pytest

from utils import parse


def test_well_formed_data():
    message = "201302018759:1890"
    factory, value = parse(message)
    assert factory == "201302018759"
    assert value == 1890


def test_empty_factory_number_should_raise_ValueError():
    message = ":333"
    with pytest.raises(ValueError):
        parse(message)


def test_factory_number_with_blank_should_raise_ValueError():
    message = "     :333"
    with pytest.raises(ValueError):
        parse(message)


def test_value_number_with_blank_should_raise_ValueError():
    message = "1234555:    "
    with pytest.raises(ValueError):
        parse(message)


def test_value_number_with_non_digit_should_raise_ValueError():
    message = "1234555:123d333"
    with pytest.raises(ValueError):
        parse(message)


