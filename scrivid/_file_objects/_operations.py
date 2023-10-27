from .. import errors

import operator


def comparison_function(attribute: str, relates: str, root: type = object):
    ops = {
        "==": operator.eq,
        ">=": operator.ge,
        ">": operator.gt,
        "<=": operator.le,
        "<": operator.lt,
        "!=": operator.ne
    }

    def function(a, b):
        if not isinstance(b, root):
            raise TypeError(f"Expected type {a.__class__.__name__}, got type {b.__class__.__name__}")
        return ops[relates](getattr(a, attribute), getattr(b, attribute))

    return function


def return_not_implemented():
    def function(_, __):
        return NotImplemented

    return function


def should_raise_operator_error(correct: str, reverse: str):
    def function(a, _):
        raise errors.OperatorError(
            f"{a.__class__.__name__} does not support \'{correct}\'.\n"
            f"\t:tip: Try reversing the operation (\'{reverse}\')."
        )

    return function
