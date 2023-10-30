from __future__ import annotations

from .._utils.sentinel_objects import sentinel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union


EXCLUDED = sentinel("EXCLUDED")


class Properties:
    __slots__ = ("layer", "scale", "x", "y")

    def __init__(
            self, *,
            layer: Union[int, EXCLUDED] = EXCLUDED,
            scale: Union[float, int, EXCLUDED] = EXCLUDED,
            x: Union[int, EXCLUDED] = EXCLUDED,
            y: Union[int, EXCLUDED] = EXCLUDED
    ):
        self.layer = layer
        self.scale = scale
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.__class__.__name__}(layer={self.layer}, scale={self.scale}, x={self.x}, y={self.y})"


def properties(
        *,
        layer: Union[int, EXCLUDED] = EXCLUDED,
        scale: Union[float, int, EXCLUDED] = EXCLUDED,
        x: Union[int, EXCLUDED] = EXCLUDED,
        y: Union[int, EXCLUDED] = EXCLUDED
):
    return Properties(layer=layer, scale=scale, x=x, y=y)
