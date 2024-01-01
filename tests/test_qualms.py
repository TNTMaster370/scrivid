from functions import get_current_directory, relational_unpacking

from scrivid import create_image_reference, qualms

import textwrap

import pytest


# ALIAS
parametrize = pytest.mark.parametrize


directory = get_current_directory() / "images"


class Coordinates:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


def force_lookup(cls, value):
    return cls.__dict__[value]


# =============================================================================
#                                SETUP OBJECTS
# =============================================================================
# `Setup` objects define the necessary set-up for testing a specific qualm
# object. This is defined in a way that allows creating a unique test function
# for each qualms, which requires multiple set-ups that a matrix-strategy is
# not compatible with.
# =============================================================================


class Setup_DrawingConfliction:
    args = "coords"
    matching_coordinates = [
        (Coordinates(256, 256), Coordinates(256, 256)),  # Exact same spot
        (Coordinates(256, 256), Coordinates(156, 156)),  # Offset, top-left
        (Coordinates(256, 256), Coordinates(411, 156)),  # Offset: top-right
        (Coordinates(256, 256), Coordinates(156, 411)),  # Offset: bot-left
        (Coordinates(256, 256), Coordinates(411, 411)),  # Offset: bot-right
    ]
    non_matching_coordinates = [
        (Coordinates(256, 256), Coordinates(0, 0)),  # Top-Left
        (Coordinates(256, 256), Coordinates(256, 0)),  # Top
        (Coordinates(256, 256), Coordinates(512, 0)),  # Top-Right
        (Coordinates(256, 256), Coordinates(512, 256)),  # Right
        (Coordinates(256, 256), Coordinates(512, 512)),  # Bottom-Right
        (Coordinates(256, 256), Coordinates(256, 512)),  # Bottom
        (Coordinates(256, 256), Coordinates(0, 512)),  # Bottom-Left
        (Coordinates(256, 256), Coordinates(0, 256)),  # Left
    ]
    relevant_class = qualms.DrawingConfliction

    @staticmethod
    def _args_a(a):
        return create_image_reference(
            1,
            directory / "img1.png",
            x=a.x,
            y=a.y
        )

    @staticmethod
    def _args_b(b):
        return create_image_reference(
            2,
            directory / "img2.png",
            x=b.x,
            y=b.y
        )

    @staticmethod
    def _args_c(c):
        return create_image_reference(
            3,
            directory / "img3.png",
            x=c.x,
            y=c.y
        )

    @classmethod
    def unpack(cls, matches, indexes):
        coordinates = force_lookup(cls, f"{'non_' if not matches else ''}matching_coordinates")
        first_arg = force_lookup(cls, f"_args_{indexes[0]}")
        second_arg = force_lookup(cls, f"_args_{indexes[1]}")
        unpacked_coordinates = []

        for a, b in coordinates:
            unpacked_coordinates.append((first_arg(a), second_arg(b)))

        return unpacked_coordinates


class Setup_OutOfRange:
    matching_coordinates = [
        Coordinates(-100, -100), Coordinates(122, -100), Coordinates(345, -100), Coordinates(345, 122),
        Coordinates(345, 345), Coordinates(122, 345), Coordinates(-100, 345), Coordinates(-100, 122)
    ]
    non_matching_coordinates = [Coordinates(100, 100)]
    relevant_class = qualms.OutOfRange
    window_size = (500, 500)

    @staticmethod
    def _args_a(a):
        return create_image_reference(
            1,
            directory / "img1.png",
            x=a.x,
            y=a.y
        )

    @classmethod
    def unpack(cls, matches, index):
        coordinates = force_lookup(cls, f"{'non_' if not matches else ''}matching_coordinates")
        arg = force_lookup(cls, f"_args_{index}")
        unpacked_coordinates = []

        for a in coordinates:
            unpacked_coordinates.append((arg(a), cls.window_size))

        return unpacked_coordinates


# =============================================================================
#                                ACTUAL  TESTS
# =============================================================================


MATCHING_CONDITIONS = [
    *relational_unpacking(qualms.DrawingConfliction, Setup_DrawingConfliction.unpack(True, "ab")),
    *relational_unpacking(qualms.OutOfRange, Setup_OutOfRange.unpack(True, "a"))
]


@parametrize("cls,args", MATCHING_CONDITIONS)
def test_check_match(cls, args):
    qualms = []
    cls.check(qualms, 0, *args)
    assert len(qualms) == 1 and isinstance(qualms[0], cls)


@parametrize("cls,args", MATCHING_CONDITIONS)
def test_check_multiple_match_aligned(cls, args):
    qualms = []
    cls.check(qualms, 1, *args)
    cls.check(qualms, 2, *args)

    assert (
        len(qualms) == 1
        and isinstance(qualms[0], cls)
        and qualms[0].index.start == 1
        and qualms[0].index.end == 2
    )


@parametrize("cls,args", MATCHING_CONDITIONS)
def test_check_multiple_match_unaligned(cls, args):
    qualms = []
    cls.check(qualms, 1, *args)
    cls.check(qualms, 3, *args)

    assert (
        len(qualms) == 2
        and isinstance(qualms[0], cls)
        and isinstance(qualms[1], cls)
    )


@parametrize("cls,args", [
    *relational_unpacking(qualms.DrawingConfliction, Setup_DrawingConfliction.unpack(False, "ab")),
    *relational_unpacking(qualms.OutOfRange, Setup_OutOfRange.unpack(False, "a"))
])
def test_check_no_match(cls, args):
    qualms = []
    cls.check(qualms, 0, *args)
    assert qualms == []


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
