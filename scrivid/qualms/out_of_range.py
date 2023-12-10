from __future__ import annotations

from ._coordinates import ImageCoordinates
from .interface import QualmInterface

import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.images import ImageReference

    from typing import List, Tuple


class OutOfRange(QualmInterface):
    __slots__ = ("image",)

    code = "D102"
    severity = 3

    def __init__(self, image: ImageReference):
        self.image = image

    def __repr__(self) -> str:
        image = self.image

        return f"{self.__class__.__name__}({image=})"

    def _message(self) -> str:
        return textwrap.dedent(f"""
            image with ID \'{self.image.ID}\' may be printed outside of canvas 
            boundaries
        """).replace("\n", "")

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
            qualms.append(cls(image))
            return

        if a.x_prime > window_size[0] or a.y_prime > window_size[1]:
            qualms.append(cls(image))
            return
