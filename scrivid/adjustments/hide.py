from __future__ import annotations

from ._type_check import check_hashable, check_int
from .core import HideAdjustment

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Hashable


def create(ID: Hashable, activation_time: int) -> HideAdjustment:
    check_hashable("ID", ID)
    check_int("activation_time", activation_time)
    return HideAdjustment(ID, activation_time)
