from __future__ import annotations

from . import images
from .. import errors
from ._operations import comparison_function, return_not_implemented, should_raise_operator_error

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable


class RootAdjustment:
    __slots__ = ("_activation_time", "_ID")

    def __init__(self, ID: Hashable, activation_time: int):
        self._activation_time = activation_time
        self._ID = ID

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._ID!r}, activation_time={self._activation_time!r})"

    def __hash__(self):
        return hash((self._ID, self._activation_time))

    """ self << other """
    __lshift__ = return_not_implemented()  # This function does not handle the
    # error that should be raised for incorrect syntax, because doing so in the
    # forward function would be too eager. If someone inherits from
    # ImageReference and wants this syntax to work, we should give it a chance
    # to invoke the reverse method.

    def __rlshift__(self, other):
        """ other << self """
        if not isinstance(other, images.ImageReference):
            raise errors.TypeError(f"Expected types ImageReference, got type {other.__name__}")
        other.add_adjustment(self)

    def __rshift__(self, other):
        """ self >> other """
        if not isinstance(other, images.ImageReference):
            raise errors.TypeError(f"Expected types ImageReference, got type {other.__name__}")
        other.add_adjustment(self)

    """ other >> self """
    __rrshift__ = should_raise_operator_error(correct=">>", reverse="<<")

    @property
    def activation_time(self):
        return self._activation_time

    @property
    def id(self):
        return self._ID

    @property
    def ID(self):
        return self._ID


""" self == other """
RootAdjustment.__eq__ = comparison_function("_activation_time", "==", RootAdjustment)

""" self >= other """
RootAdjustment.__ge__ = comparison_function("_activation_time", ">=", RootAdjustment)

""" self > other """
RootAdjustment.__gt__ = comparison_function("_activation_time", ">", RootAdjustment)

""" self <= other """
RootAdjustment.__le__ = comparison_function("_activation_time", "<=", RootAdjustment)

""" self < other """
RootAdjustment.__lt__ = comparison_function("_activation_time", "<", RootAdjustment)

""" self != other """
RootAdjustment.__ne__ = comparison_function("_activation_time", "!=", RootAdjustment)


class HideAdjustment(RootAdjustment):
    ...


class ShowAdjustment(RootAdjustment):
    ...
