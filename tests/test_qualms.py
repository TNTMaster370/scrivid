from functions import get_current_directory

from scrivid import create_image_reference, qualms

import pytest


# ALIAS
DrawingConfliction = qualms.DrawingConfliction
parametrize = pytest.mark.parametrize


directory = get_current_directory() / "images"


class _Coordinates:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


class TestDrawingConfliction:
    @staticmethod
    def _get_check(a, b):
        image_a = create_image_reference(
            1,
            directory / "img1.png",
            x=a.x,
            y=a.y
        )
        image_b = create_image_reference(
            2,
            directory / "img2.png",
            x=b.x,
            y=b.y
        )
        qualms = []
        DrawingConfliction.check(qualms, image_a, image_b)

        return qualms

    @parametrize("a,b", [
        (_Coordinates(256, 256), _Coordinates(256, 256)),  # Same spot
        (_Coordinates(256, 256), _Coordinates(156, 156)),  # Offset, top-left
        (_Coordinates(256, 256), _Coordinates(411, 156)),  # Offset: top-right
        (_Coordinates(256, 256), _Coordinates(156, 411)),  # Offset: bot-left
        (_Coordinates(256, 256), _Coordinates(411, 411)),  # Offset: bot-right
    ])
    def test_match(self, a, b):
        result = self._get_check(a, b)
        assert len(result) == 1 and isinstance(result[0], DrawingConfliction)

    @parametrize("a,b", [
        (_Coordinates(256, 256), _Coordinates(0, 0)),  # Top-Left
        (_Coordinates(256, 256), _Coordinates(256, 0)),  # Top
        (_Coordinates(256, 256), _Coordinates(512, 0)),  # Top-Right
        (_Coordinates(256, 256), _Coordinates(512, 256)),  # Right
        (_Coordinates(256, 256), _Coordinates(512, 512)),  # Bottom-Right
        (_Coordinates(256, 256), _Coordinates(256, 512)),  # Bottom
        (_Coordinates(256, 256), _Coordinates(0, 512)),  # Bottom-Left
        (_Coordinates(256, 256), _Coordinates(0, 256)),  # Left
    ])
    def test_no_match(self, a, b):
        result = self._get_check(a, b)
        assert result == []
