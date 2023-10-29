from __future__ import annotations

from ._operations import comparison_function

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
