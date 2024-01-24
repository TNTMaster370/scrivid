from __future__ import annotations

from ._type_check import check_hashable, check_inheritance, check_int
from .core import MoveAdjustment

from .._file_objects.properties import Properties

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Hashable


def create(ID: Hashable, activation_time: int, change: Properties, duration: int) -> MoveAdjustment:
    check_hashable("ID", ID)
    check_int("activation_time", activation_time)
    check_inheritance("change", change, Properties)
    check_int("duration", duration)

    return MoveAdjustment(ID, activation_time, change, duration)
