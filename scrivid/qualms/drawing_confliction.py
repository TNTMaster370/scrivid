from __future__ import annotations

from ._coordinates import ImageCoordinates
from .interface import QualmInterface

import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.images import ImageReference

    from typing import List


def _above(a: ImageCoordinates, b: ImageCoordinates):
    return a.y_prime < b.y


def _left_of(a: ImageCoordinates, b: ImageCoordinates):
    return a.x_prime < b.x


class DrawingConfliction(QualmInterface):
    __slots__ = ("image_a", "image_b")

    code = "D101"
    severity = 4

    def __init__(self, image_a: ImageReference, image_b: ImageReference):
        self.image_a = image_a
        self.image_b = image_b

    def __repr__(self):
        image_a = self.image_a
        image_b = self.image_b

        return f"{self.__class__.__name__}({image_a=}, {image_b=})"

    def _message(self) -> str:
        return textwrap.dedent(f"""
            images with IDs \'{self.image_a.ID}\' and \'{self.image_b.ID}\' 
            overlap with each other
        """).replace("\n", "")

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

        qualms.append(cls(image_a, image_b))
