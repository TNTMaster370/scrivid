from functions import categorize, get_current_directory, unwrap_string

from scrivid import create_image_reference, errors, qualms

from abc import ABC, abstractmethod
import itertools

import pytest


# ALIAS
parametrize = pytest.mark.parametrize


directory = get_current_directory() / "images"

IMAGE_LIMIT = 3


def assemble_qualm_args(*setup_classes, matches, count=1):
    args = []

    for setup_class in setup_classes:
        current_args = []

        for count_index in range(count):
            current_args.append(setup_class.fully_unpack_coordinates(count_index, matches))

        current_args = transpose(*current_args)
        for a, b in itertools.product((setup_class.relevant_class,), current_args):
            args.append((a, *b))

    return args


class Coordinates:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


def force_lookup(cls, value):
    return cls.__dict__[value]


def initialize_image_reference(index, coordinates=None):
    kwargs = {}

    if coordinates is not None:
        kwargs = {"x": coordinates.x, "y": coordinates.y}

    return create_image_reference(index, directory / f"img{index}.png", **kwargs)


def transpose(*i):
    return tuple(i_ for i_ in zip(*i))


# =============================================================================
#                                SETUP OBJECTS
# =============================================================================
# `Setup` objects define the necessary set-up for testing a specific qualm
# object. This is defined in a way that allows creating a unique test function
# for each qualms, which requires multiple set-ups that a matrix-strategy is
# not compatible with.
# =============================================================================


class BaseSetup(ABC):
    matching_coordinates: list
    non_matching_coordinates: list
    relevant_class: qualms

    @classmethod
    def fully_unpack_coordinates(cls, index, matching):
        coordinates = getattr(cls, f"{'non_' if not matching else ''}matching_coordinates")
        args = []

        for coordinate in coordinates:
            args.append(cls.invoke_coordinates(coordinate, index))

        # return ((cls.relevant_class,), args)
        return args

    @classmethod
    @abstractmethod
    def invoke_coordinates(cls):
        raise NotImplementedError


class Setup_DrawingConfliction(BaseSetup):
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

    @classmethod
    def invoke_coordinates(cls, coordinate, index):
        args_a = initialize_image_reference((index % IMAGE_LIMIT) + 1, coordinate[0])
        args_b = initialize_image_reference((index % IMAGE_LIMIT) + 2, coordinate[1])
        return (args_a, args_b)


class Setup_OutOfRange(BaseSetup):
    matching_coordinates = [
        Coordinates(-100, -100), Coordinates(122, -100), Coordinates(345, -100), Coordinates(345, 122),
        Coordinates(345, 345), Coordinates(122, 345), Coordinates(-100, 345), Coordinates(-100, 122)
    ]
    non_matching_coordinates = [Coordinates(100, 100)]
    relevant_class = qualms.OutOfRange
    window_size = (500, 500)

    @classmethod
    def invoke_coordinates(cls, coordinate, index):
        args_a = initialize_image_reference((index % IMAGE_LIMIT) + 1, coordinate)
        return (args_a, cls.window_size)


SETUP_CLASSES = (Setup_DrawingConfliction, Setup_OutOfRange)


# =============================================================================
#                                ACTUAL  TESTS
# =============================================================================


MATCHING_CONDITIONS = assemble_qualm_args(*SETUP_CLASSES, matches=True)


@categorize(category="qualms")
@parametrize("cls,args", MATCHING_CONDITIONS)
def test_check_match(cls, args):
    qualms = []
    cls.check(qualms, 0, *args)
    assert len(qualms) == 1 and isinstance(qualms[0], cls)


@categorize(category="qualms")
@parametrize("cls,args", MATCHING_CONDITIONS)
def test_check_multiple_match_aligned(cls, args):
    qualms = []

    for time in (1, 2):
        cls.check(qualms, time, *args)

    assert (
        len(qualms) == 1
        and isinstance(qualms[0], cls)
        and qualms[0].index.start == 1
        and qualms[0].index.end == 2
    )


@categorize(category="qualms")
@parametrize("cls,args_q,args_r", assemble_qualm_args(*SETUP_CLASSES, count=2, matches=True))
def test_check_multiple_match_different_args(cls, args_q, args_r):
    qualms = []
    combination = "qrq"  # The `combination` variable refers to the order of
    # the args used in the matching.

    for char, time in zip(combination, (1, 1, 2)):
        args = args_q if char == "q" else args_r
        cls.check(qualms, time, *args)

    assert (
        len(qualms) == 2
        and isinstance(qualms[0], cls)
        and isinstance(qualms[1], cls)
        and qualms[0].index.start == 1
        and qualms[0].index.end == 2
    )


@categorize(category="qualms")
@parametrize("cls,args", MATCHING_CONDITIONS)
def test_check_multiple_match_unaligned(cls, args):
    qualms = []

    for time in (1, 3):
        cls.check(qualms, time, *args)

    assert (
        len(qualms) == 2
        and isinstance(qualms[0], cls)
        and isinstance(qualms[1], cls)
    )


@categorize(category="qualms")
@parametrize("cls,args", assemble_qualm_args(*SETUP_CLASSES, matches=False))
def test_check_no_match(cls, args):
    qualms = []
    cls.check(qualms, 0, *args)
    assert qualms == []


IMG_REF_A = initialize_image_reference(1)
IMG_REF_B = initialize_image_reference(2)
IMG_REF_C = initialize_image_reference(3)


@categorize(category="qualms")
@parametrize("qualm_a,args_a,qualm_b,args_b", [
    (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B), qualms.OutOfRange, (IMG_REF_A,)),
    (qualms.OutOfRange, (IMG_REF_A,), qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B))
])
def test_comparison_different_types(qualm_a, args_a, qualm_b, args_b):
    qualm_object_a = qualm_a(0, *args_a)
    qualm_object_b = qualm_b(0, *args_b)

    assert (qualm_object_a == qualm_object_b) is False


@categorize(category="qualms")
@parametrize("qualm,args_a,args_b", [
    (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B), (IMG_REF_A, IMG_REF_C)),
    (qualms.OutOfRange, (IMG_REF_A,), (IMG_REF_B,))
])
def test_comparison_false(qualm, args_a, args_b):
    qualm_object_a = qualm(0, *args_a)
    qualm_object_b = qualm(0, *args_b)

    assert (qualm_object_a == qualm_object_b) is False


@categorize(category="qualms")
@parametrize("qualm,args", [
    (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B)),
    (qualms.OutOfRange, (IMG_REF_A,))
])
def test_comparison_invalid_type(qualm, args):
    qualm_object = qualm(0, *args)
    wrong_type = "STRING IS NOT VALID."

    with pytest.raises(errors.TypeError):
        qualm_object == wrong_type


@categorize(category="qualms")
@parametrize("qualm,args", [
    (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B)),
    (qualms.OutOfRange, (IMG_REF_A,))
])
def test_comparison_true(qualm, args):
    qualm_object_a = qualm(0, *args)
    qualm_object_b = qualm(0, *args)

    assert (qualm_object_a == qualm_object_b) is True


@categorize(category="qualms")
@parametrize("qualm,expected", [
    (qualms.DrawingConfliction(
        0,
        create_image_reference("1", ""),
        create_image_reference("2", "")
     ),
     ":D101:4: images with IDs \'1\' and \'2\' overlap with each other"),
    (qualms.OutOfRange(0, create_image_reference("1", "")),
     unwrap_string("""
        :D102:3: image with ID \'1\' may be printed outside of canvas 
        boundaries
     """)),
])
def test_message(qualm, expected):
    assert str(qualm) == expected
