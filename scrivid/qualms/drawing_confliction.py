from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.images import ImageReference


def _above(a: _Coordinates, b: _Coordinates):
    return a.y_prime < b.y


class _Coordinates:
    __slots__ = ("x", "x_prime", "y", "y_prime")

    def __init__(self, x, y, width, height):
        self.x = x
        self.x_prime = x + width
        self.y = y
        self.y_prime = y + height


def _left_of(a: _Coordinates, b: _Coordinates):
    return a.x_prime < b.x


class DrawingConfliction:
    __slots__ = ()

    @classmethod
    def check(cls, image_a: ImageReference, image_b: ImageReference):
        if not image_a.is_opened:
            image_a.open()
        if not image_b.is_opened:
            image_b.open()

        a = _Coordinates(
            image_a.x,
            image_a.y,
            image_a.get_image_width(),
            image_a.get_image_height()
        )
        b = _Coordinates(
            image_b.x,
            image_b.y,
            image_b.get_image_width(),
            image_b.get_image_height()
        )

        if _left_of(a, b) or _left_of(b, a):
            return

        if _above(a, b) or _above(b, a):
            return

        return cls()
