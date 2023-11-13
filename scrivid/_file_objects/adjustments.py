from __future__ import annotations

from ._operations import comparison_function
from ._status import VisibilityStatus
from .properties import EXCLUDED, Properties

from abc import ABC, abstractmethod
from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable, Union


def _increment_value(full_value: Union[float, int, EXCLUDED], duration: int, length: int, precision: Union[float, int]):
    if full_value is EXCLUDED:
        return full_value

    value, remainder = divmod(full_value, duration)
    value *= length
    remainder *= length

    excess_precision = remainder // precision
    if excess_precision < 1:
        return value

    return value + (remainder - (excess_precision * precision))


class RootAdjustment(ABC):
    __slots__ = ("_activation_time", "_ID")

    def __init__(self, ID: Hashable, activation_time: int):
        self._activation_time = activation_time
        self._ID = ID

    def __repr__(self):
        id = self._ID
        activation_time = self._activation_time

        return f"{self.__class__.__name__}({id=!r}, {activation_time=!r})"

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

    @abstractmethod
    def _enact(self) -> Properties:
        ...


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
    def _enact(self) -> Properties:
        return Properties(visibility=VisibilityStatus.HIDE)


class MoveAdjustment(RootAdjustment):
    __slots__ = ("_change", "_duration")

    def __init__(self, ID: Hashable, activation_time: int, change: Properties, duration: int):
        super().__init__(ID, activation_time)
        self._change = change
        self._duration = duration

    def __repr__(self):
        change = self._change
        duration = self._duration

        return f"{super().__repr__()[:-1]}, {change=!r}, {duration=!r})"

    @property
    def change(self):
        return self._change

    @property
    def duration(self):
        return self._duration

    def _enact(self, length: int) -> Properties:
        if self._duration == 1 or self._duration == length:
            return self._change
        else:
            return self._split_change(length)

    def _split_change(self, length: int = 1) -> Properties:
        scale = _increment_value(self._change.scale, self._duration, length, 0.1)
        x = _increment_value(self._change.x, self._duration, length, 1)
        y = _increment_value(self._change.y, self._duration, length, 1)

        return Properties(scale=scale, x=x, y=y)


class ShowAdjustment(RootAdjustment):
    def _enact(self) -> Properties:
        return Properties(visibility=VisibilityStatus.SHOW)
