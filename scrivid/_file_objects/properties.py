from __future__ import annotations

from ._status import VisibilityStatus
from .. import errors
from .._utils.sentinel_objects import sentinel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union


EXCLUDED = sentinel("EXCLUDED")


class Properties:
    __slots__ = ("layer", "scale", "visibility", "x", "y")

    def __init__(
            self, *,
            layer: Union[int, EXCLUDED] = EXCLUDED,
            scale: Union[float, int, EXCLUDED] = EXCLUDED,
            visibility: Union[VisibilityStatus, EXCLUDED] = EXCLUDED,
            x: Union[int, EXCLUDED] = EXCLUDED,
            y: Union[int, EXCLUDED] = EXCLUDED
    ):
        self.layer = layer
        self.scale = scale
        self.visibility = visibility
        self.x = x
        self.y = y

    def __repr__(self):
        layer = self.layer
        scale = self.scale
        visibility = self.visibility
        x = self.x
        y = self.y
        return (
            f"{self.__class__.__name__}({layer=}, {scale=}, {visibility=}, {x=}, {y=})"
        )

    def __and__(self, other):
        return self.merge(other)

    def _check_confliction(self, other):
        if not isinstance(other, Properties):
            raise errors.TypeError(f"Expected Properties object, got type {type(other)}.")

        NO_RETURN = sentinel("NO_RETURN")

        for attr in self.__slots__:
            a = getattr(self, attr, NO_RETURN)
            b = getattr(other, attr, NO_RETURN)

            if a is NO_RETURN:
                raise errors.AttributeError(
                    f"Attribute \'{attr}\' not found in {self.__class__.__name__} instance \'{self}\'"
                )
            elif b is NO_RETURN:
                raise errors.AttributeError(
                    f"Attribute \'{attr}\' not found in {other.__class__.__name__} instance \'{other}\'"
                )

            if (EXCLUDED in (a, b)) or (a == b):
                continue

            raise errors.AttributeError(f"Attribute confliction (\'{attr}\'): {a=}, {b=}")

    def merge(self, other: Properties, /, *, strict: bool = True):
        if strict:
            self._check_confliction(other)
        return self.__class__(
            layer=self.layer if self.layer is not EXCLUDED else other.layer,
            scale=self.scale if self.scale is not EXCLUDED else other.scale,
            visibility=self.visibility if self.visibility is not EXCLUDED else other.visibility,
            x=self.x if self.x is not EXCLUDED else other.x,
            y=self.y if self.y is not EXCLUDED else other.y
        )


def properties(
        *,
        layer: Union[int, EXCLUDED] = EXCLUDED,
        scale: Union[float, int, EXCLUDED] = EXCLUDED,
        visibility: Union[VisibilityStatus, EXCLUDED] = EXCLUDED,
        x: Union[int, EXCLUDED] = EXCLUDED,
        y: Union[int, EXCLUDED] = EXCLUDED
):
    # Define default values for non-required variables. If it's intended to be
    # used specifically for merging, you may wish to instantiate it directly,
    # instead of using this factory function.
    if visibility is EXCLUDED:
        visibility = VisibilityStatus.SHOW
    return Properties(layer=layer, scale=scale, visibility=visibility, x=x, y=y)
