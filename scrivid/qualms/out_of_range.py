from __future__ import annotations

from ._coordinates import ImageCoordinates
from .interface import QualmInterface

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.images import ImageReference

    from typing import List, Tuple


class OutOfRange(QualmInterface):
    __slots__ = ()

    @classmethod
    def check(
            cls,
            qualms: List[QualmInterface],
            image: ImageReference,
            window_size: Tuple[int, int]
    ):
        if not image.is_opened:
            image.open()

        a = ImageCoordinates(image)

        if a.x < 0 or a.y < 0:
            qualms.append(cls())
            return

        if a.x_prime > window_size[0] or a.y_prime > window_size[1]:
            qualms.append(cls())
            return
