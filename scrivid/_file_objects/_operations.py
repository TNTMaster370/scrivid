from .. import errors


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
