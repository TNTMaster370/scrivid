class ScrividException(Exception):
    # Base class for all Exceptions that is used by Scrivid.
    ...


class AttributeError(ScrividException):
    ...


class InvalidAttributesError(AttributeError):
    ...


class UndefinedAttributesError(AttributeError):
    ...


class OperatorError(ScrividException):
    ...


class TypeError(ScrividException):
    ...
