from functions import get_current_directory, relational_unpacking

from scrivid import create_image_reference, errors, qualms

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
    def unpack(cls, arg, constructor_index):
        constructor_a = force_lookup(cls, f"_args_{constructor_index[0]}")
        constructor_b = force_lookup(cls, f"_args_{constructor_index[1]}")
        return (constructor_a(arg[0]), constructor_b(arg[1]))


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
    def unpack(cls, arg, constructor_index):
        constructor = force_lookup(cls, f"_args_{constructor_index}")
        return (constructor(arg), cls.window_size)


# =============================================================================
#                                ACTUAL  TESTS
# =============================================================================


MATCHING_CONDITIONS = [
    *relational_unpacking(Setup_DrawingConfliction, Setup_DrawingConfliction.matching_coordinates, "ab"),
    *relational_unpacking(Setup_OutOfRange, Setup_OutOfRange.matching_coordinates, "a")
]


@parametrize("setup_class,arguments,constructor_indexes", MATCHING_CONDITIONS)
def test_check_match(setup_class, arguments, constructor_indexes):
    args = setup_class.unpack(arguments, constructor_indexes)
    cls = setup_class.relevant_class
    qualms = []

    cls.check(qualms, 0, *args)
    assert len(qualms) == 1 and isinstance(qualms[0], cls)


@parametrize("setup_class,arguments,constructor_indexes", MATCHING_CONDITIONS)
def test_check_multiple_match_aligned(setup_class, arguments, constructor_indexes):
    args = setup_class.unpack(arguments, constructor_indexes)
    cls = setup_class.relevant_class
    qualms = []

    for time in (1, 2):
        cls.check(qualms, time, *args)

    assert (
        len(qualms) == 1
        and isinstance(qualms[0], cls)
        and qualms[0].index.start == 1
        and qualms[0].index.end == 2
    )


@parametrize("setup_class,arguments,constructor_indexes", MATCHING_CONDITIONS)
def test_check_multiple_match_unaligned(setup_class, arguments, constructor_indexes):
    args = setup_class.unpack(arguments, constructor_indexes)
    cls = setup_class.relevant_class
    qualms = []

    for time in (1, 3):
        cls.check(qualms, time, *args)

    assert (
        len(qualms) == 2
        and isinstance(qualms[0], cls)
        and isinstance(qualms[1], cls)
    )


@parametrize("setup_class,arguments,constructor_indexes", [
    *relational_unpacking(Setup_DrawingConfliction, Setup_DrawingConfliction.non_matching_coordinates, "ab"),
    *relational_unpacking(Setup_OutOfRange, Setup_OutOfRange.non_matching_coordinates, "a")
])
def test_check_no_match(setup_class, arguments, constructor_indexes):
    args = setup_class.unpack(arguments, constructor_indexes)
    cls = setup_class.relevant_class
    qualms = []

    cls.check(qualms, 0, *args)
    assert qualms == []


IMG_REF_A = create_image_reference(1, directory / "img1.png")
IMG_REF_B = create_image_reference(2, directory / "img2.png")
IMG_REF_C = create_image_reference(3, directory / "img3.png")


@parametrize("qualm_a,args_a,qualm_b,args_b", [
    (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B), qualms.OutOfRange, (IMG_REF_A,)),
    (qualms.OutOfRange, (IMG_REF_A,), qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B))
])
def test_comparison_different_types(qualm_a, args_a, qualm_b, args_b):
    qualm_object_a = qualm_a(0, *args_a)
    qualm_object_b = qualm_b(0, *args_b)

    assert (qualm_object_a == qualm_object_b) is False


@parametrize("qualm,args_a,args_b", [
    (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B), (IMG_REF_A, IMG_REF_C)),
    (qualms.OutOfRange, (IMG_REF_A,), (IMG_REF_B,))
])
def test_comparison_false(qualm, args_a, args_b):
    qualm_object_a = qualm(0, *args_a)
    qualm_object_b = qualm(0, *args_b)

    assert (qualm_object_a == qualm_object_b) is False


@parametrize("qualm,args", [
    (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B)),
    (qualms.OutOfRange, (IMG_REF_A,))
])
def test_comparison_invalid_type(qualm, args):
    qualm_object = qualm(0, *args)
    wrong_type = "STRING IS NOT VALID."

    with pytest.raises(errors.TypeError):
        qualm_object == wrong_type


@parametrize("qualm,args", [
    (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B)),
    (qualms.OutOfRange, (IMG_REF_A,))
])
def test_comparison_true(qualm, args):
    qualm_object_a = qualm(0, *args)
    qualm_object_b = qualm(0, *args)

    assert (qualm_object_a == qualm_object_b) is True


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
