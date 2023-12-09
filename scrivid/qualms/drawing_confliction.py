from __future__ import annotations

from ._coordinates import ImageCoordinates
from .interface import QualmInterface

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.images import ImageReference

    from typing import List


def _above(a: ImageCoordinates, b: ImageCoordinates):
    return a.y_prime < b.y


def _left_of(a: ImageCoordinates, b: ImageCoordinates):
    return a.x_prime < b.x


class DrawingConfliction(QualmInterface):
    __slots__ = ()

    @classmethod
    def check(
            cls,
            qualms: List[QualmInterface],
            image_a: ImageReference,
            image_b: ImageReference
    ):
        if not image_a.is_opened:
            image_a.open()
        if not image_b.is_opened:
            image_b.open()

        a = ImageCoordinates(image_a)
        b = ImageCoordinates(image_b)

        if _left_of(a, b) or _left_of(b, a):
            return

        if _above(a, b) or _above(b, a):
            return

        qualms.append(cls())
