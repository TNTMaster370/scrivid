from scrivid import errors

import inspect
import sys

import pytest


# Alternative name for module to reduce typing
pytest_parametrize = pytest.mark.parametrize


def loop_over_namespace(namespace):
    namespace = sys.modules[namespace].__dict__.copy()
    for name in namespace:
        if name.startswith("__") and name.endswith("__"):
            continue
        elif not inspect.isclass(name):
            continue
        yield name


@pytest_parametrize("exception,kwargs", [
    (errors.ConflictingAttributesError, 
     {"first_name": "first_name", "first_value": "first_value", "second_name": "second_name", 
      "second_value": "second_value"})
])
def test_exceptions_default_message(exception, kwargs):
    exc = exception(**kwargs)
    default_message = exception.default_message.replace("{", "").replace("}", "")
    assert exc.message == default_message


def test_exceptions_inheritance():
    for name in loop_over_namespace(errors.__name__):
        if name == errors.ScrividException.__name__:
            continue
        assert isinstance(name, errors.ScrividException)
