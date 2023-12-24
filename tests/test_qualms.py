from functions import get_current_directory

from scrivid import create_image_reference, qualms

from abc import ABC, abstractmethod
import textwrap

import pytest


# ALIAS
parametrize = pytest.mark.parametrize


directory = get_current_directory() / "images"


class _Coordinates:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


class _QualmsTests(ABC):
    @abstractmethod
    def _get_args(self, args):
        ...

    def test_match(self, args):
        cls = self.relevant_class
        qualms = []

        cls.check(qualms, 0, *args)
        assert len(qualms) == 1 and isinstance(qualms[0], cls)

    def test_multiple_match_aligned(self, args):
        cls = self.relevant_class
        qualms = []

        cls.check(qualms, 1, *args)
        cls.check(qualms, 2, *args)

        assert (
            len(qualms) == 1
            and isinstance(qualms[0], cls)
            and qualms[0].index.start == 1
            and qualms[0].index.end == 2
        )

    def test_multiple_match_unaligned(self, args):
        cls = self.relevant_class
        qualms = []

        cls.check(qualms, 1, *args)
        cls.check(qualms, 3, *args)

        assert (
            len(qualms) == 2
            and isinstance(qualms[0], cls)
            and isinstance(qualms[1], cls)
        )

    def test_no_match(self, args):
        cls = self.relevant_class
        qualms = []

        cls.check(qualms, 0, *args)
        assert qualms == []


class TestDrawingConfliction(_QualmsTests):
    matching_coordinates = [
        (_Coordinates(256, 256), _Coordinates(256, 256)),  # Same spot
        (_Coordinates(256, 256), _Coordinates(156, 156)),  # Offset, top-left
        (_Coordinates(256, 256), _Coordinates(411, 156)),  # Offset: top-right
        (_Coordinates(256, 256), _Coordinates(156, 411)),  # Offset: bot-left
        (_Coordinates(256, 256), _Coordinates(411, 411)),  # Offset: bot-right
    ]
    relevant_class = qualms.DrawingConfliction

    def _get_args(self, a, b):
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
        return image_a, image_b

    @parametrize("a,b", matching_coordinates)
    def test_match(self, a, b):
        super().test_match(self._get_args(a, b))

    @parametrize("a,b", matching_coordinates)
    def test_multiple_match_aligned(self, a, b):
        super().test_multiple_match_aligned(self._get_args(a, b))

    @parametrize("a,b", matching_coordinates)
    def test_multiple_match_unaligned(self, a, b):
        super().test_multiple_match_unaligned(self._get_args(a, b))

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
        super().test_no_match(self._get_args(a, b))


@parametrize("qualm,expected", [
    (qualms.DrawingConfliction(
        0,
        create_image_reference("1", ""),
        create_image_reference("2", "")
     ),
     ":D101:4: images with IDs \'1\' and \'2\' overlap with each other"),
    (qualms.OutOfRange(0, create_image_reference("1", "")),
     textwrap.dedent("""
        :D102:3: image with ID \'1\' may be printed outside of canvas 
        boundaries
     """).replace("\n", "")),
])
def test_message(qualm, expected):
    assert str(qualm) == expected


class TestOutOfRange(_QualmsTests):
    matching_coordinates = [
        _Coordinates(-100, -100), _Coordinates(122, -100), _Coordinates(345, -100), _Coordinates(345, 122),
        _Coordinates(345, 345), _Coordinates(122, 345), _Coordinates(-100, 345), _Coordinates(-100, 122)
    ]
    relevant_class = qualms.OutOfRange
    window_size = (500, 500)

    def _get_args(self, a):
        return (
            create_image_reference(
                1,
                directory / "img1.png",
                x=a.x,
                y=a.y
            ), 
            self.window_size
        )

    @parametrize("a", matching_coordinates)
    def test_match(self, a):
        super().test_match(self._get_args(a))

    @parametrize("a", matching_coordinates)
    def test_multiple_match_aligned(self, a):
        super().test_multiple_match_aligned(self._get_args(a))

    @parametrize("a", matching_coordinates)
    def test_multiple_match_unaligned(self, a):
        super().test_multiple_match_unaligned(self._get_args(a))

    @parametrize("a", [_Coordinates(100, 100)])
    def test_no_match(self, a):
        super().test_no_match(self._get_args(a))
