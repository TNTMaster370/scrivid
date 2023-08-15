from scrivid import exceptions

import inspect
import sys


def loop_over_namespace(namespace):
    namespace = sys.modules[namespace].__dict__.copy()
    for name in namespace:
        if name.startswith("__") and name.endswith("__"):
            continue
        elif not inspect.isclass(name):
            continue
        yield name


def test_exceptions_inheritance():
    for name in loop_over_namespace(exceptions.__name__):
        if name == exceptions.ScrividException.__name__:
            continue
        assert isinstance(name, exceptions.ScrividException)
