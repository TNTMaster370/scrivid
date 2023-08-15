from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union


class Properties:
    __slots__ = ("layer", "scale", "x", "y")

    def __init__(self, layer: int, scale: Union[float, int], x: int, y: int):
        self.layer = layer
        self.scale = scale
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.__class__.__name__}(layer={self.layer}, scale={self.scale}, x={self.x}, y={self.y})"


def properties(*, layer: int, scale: Union[float, int], x: int, y: int):
    return Properties(layer, scale, x, y)
