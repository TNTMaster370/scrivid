from __future__ import annotations

from ._status import Status

from abc import abstractmethod


class RootAdjustment:
    __slots__ = ("_activation_time",)

    def __init__(self, activation_time: int):
        self._activation_time = activation_time

    def __repr__(self):
        return f"{self.__class__.__name__}(activation_time={self._activation_time!r})"

    def __hash__(self):
        return hash(self._activation_time)

    @property
    def activation_time(self):
        return self._activation_time

    @abstractmethod
    def utilize(self, reference):
        raise NotImplementedError


class HideAdjustment(RootAdjustment):
    def utilize(self, reference):
        reference._status = Status.HIDE


class ShowAdjustment(RootAdjustment):
    def utilize(self, reference):
        reference._status = Status.SHOW
