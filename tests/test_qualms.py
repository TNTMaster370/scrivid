from functions import get_current_directory

from scrivid import create_image_reference, qualms

import textwrap

import pytest


# ALIAS
DrawingConfliction = qualms.DrawingConfliction
parametrize = pytest.mark.parametrize
OutOfRange = qualms.OutOfRange


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


@parametrize("qualm,expected", [
    (DrawingConfliction(
        create_image_reference("1", ""),
        create_image_reference("2", "")
     ),
     ":D101:4: images with IDs \'1\' and \'2\' overlap with each other"),
    (OutOfRange(create_image_reference("1", "")),
     textwrap.dedent("""
        :D102:3: image with ID \'1\' may be printed outside of canvas 
        boundaries
     """).replace("\n", "")),
])
def test_message(qualm, expected):
    assert str(qualm) == expected


class TestOutOfRange:
    window_size = (500, 500)

    @staticmethod
    def _get_check(a, window_size):
        image_a = create_image_reference(
            1,
            directory / "img1.png",
            x=a.x,
            y=a.y
        )
        qualms = []
        OutOfRange.check(qualms, image_a, window_size)

        return qualms

    @parametrize("a", [
        _Coordinates(-100, -100), _Coordinates(122, -100),
        _Coordinates(345, -100), _Coordinates(345, 122),
        _Coordinates(345, 345), _Coordinates(122, 345),
        _Coordinates(-100, 345), _Coordinates(-100, 122),
    ])
    def test_match(self, a):
        result = self._get_check(a, self.window_size)
        assert len(result) == 1 and isinstance(result[0], OutOfRange)

    @parametrize("a", [_Coordinates(100, 100)])
    def test_no_match(self, a):
        result = self._get_check(a, self.window_size)
        assert result == []
