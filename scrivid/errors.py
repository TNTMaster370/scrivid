class ScrividException(Exception):
    """ Base class for all Exceptions that are propagated from Scrivid. """


class AttributeError(ScrividException):
    ...


class DuplicateIDError(ScrividException):
    ...


class InternalError(ScrividException):
    ...


class OperatorError(ScrividException):
    ...


class TypeError(ScrividException):
    ...
