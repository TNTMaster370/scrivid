from functions import assemble_arguments, categorize, get_current_directory

from scrivid import create_image_reference, errors, qualms

from abc import ABC, abstractmethod
import itertools

import pytest


# ALIAS
parametrize = pytest.mark.parametrize


directory = get_current_directory() / "images"

IMAGE_LIMIT = 3


def _assemble_method_permutations(*, length=2, separator=" | "):
    def function(arguments, id_convention):
        for permutation in itertools.permutations(arguments, length):
            args = []
            complete_id = ""

            for p in permutation:
                for p_ in p:
                    args.append(p_)
                complete_id += f"{id_convention(p)}{separator}"

            complete_id = complete_id[:(-1 * len(separator))]

            yield pytest.param(*args, id=complete_id)

    return function


def _assemble_method_qualm_setup(*, matches=True, count=1):
    ids_name = f"{'non_' if not matches else ''}matching_ids"

    def function(arguments, _):
        for setup_class in arguments:
            args = []
            ids = getattr(setup_class, ids_name)

            for count_index in range(count):
                args.append(setup_class.fully_unpack_coordinates(count_index, matches))

            args = transpose(*args)
            relevant_class = setup_class.relevant_class
            for arg, ids_string in zip(args, ids):
                yield pytest.param(relevant_class, *arg, id=f"{relevant_class.__name__}, \'{ids_string}\'")

    return function


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
    matching_ids: list
    non_matching_coordinates: list
    non_matching_ids: list
    relevant_class: qualms

    @classmethod
    def fully_unpack_coordinates(cls, index, matching):
        coordinates = getattr(cls, f"{'non_' if not matching else ''}matching_coordinates")
        args = []

        for coordinate in coordinates:
            args.append(cls.invoke_coordinates(coordinate, index))

        return args

    @classmethod
    @abstractmethod
    def invoke_coordinates(cls):
        raise NotImplementedError


class Setup_DrawingConfliction(BaseSetup):
    matching_coordinates = (
        (Coordinates(256, 256), Coordinates(256, 256)),
        (Coordinates(256, 256), Coordinates(156, 156)),
        (Coordinates(256, 256), Coordinates(411, 156)),
        (Coordinates(256, 256), Coordinates(156, 411)),
        (Coordinates(256, 256), Coordinates(411, 411)),
    )
    matching_ids = (
        "a in same spot as b", "b above/left of a", "b above/right of a", "b under/right of a", "b under/left of a"
    )

    non_matching_coordinates = (
        (Coordinates(256, 256), Coordinates(0, 0)),
        (Coordinates(256, 256), Coordinates(256, 0)),
        (Coordinates(256, 256), Coordinates(512, 0)),
        (Coordinates(256, 256), Coordinates(512, 256)),
        (Coordinates(256, 256), Coordinates(512, 512)),
        (Coordinates(256, 256), Coordinates(256, 512)),
        (Coordinates(256, 256), Coordinates(0, 512)),
        (Coordinates(256, 256), Coordinates(0, 256)),
    )
    non_matching_ids = (
        "b above/left of a", "b above a", "b above/right of a", "b right of a", "b under/right of a", "b under a",
        "b under/left of a", "b left of a"
    )

    relevant_class = qualms.DrawingConfliction

    @classmethod
    def invoke_coordinates(cls, coordinate, index):
        args_a = initialize_image_reference((index % IMAGE_LIMIT) + 1, coordinate[0])
        args_b = initialize_image_reference((index % IMAGE_LIMIT) + 2, coordinate[1])
        return (args_a, args_b)


class Setup_OutOfRange(BaseSetup):
    matching_coordinates = (
        Coordinates(-100, -100), Coordinates(122, -100), Coordinates(345, -100), Coordinates(345, 122),
        Coordinates(345, 345), Coordinates(122, 345), Coordinates(-100, 345), Coordinates(-100, 122)
    )
    matching_ids = (
        "a above/left of window", "a above window", "a above/right of window", "a right of window",
        "a under/right of window", "a under window", "a under/left of window", "a left of window"
    )

    non_matching_coordinates = (Coordinates(100, 100),)
    non_matching_ids = ("within window",)

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


MATCHING_CONDITIONS = assemble_arguments(*SETUP_CLASSES, id_convention=None, method=_assemble_method_qualm_setup())


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
@parametrize(
    "cls,args_q,args_r",
    assemble_arguments(*SETUP_CLASSES, id_convention=None, method=_assemble_method_qualm_setup(count=2))
)
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
@parametrize(
    "cls,args",
    assemble_arguments(*SETUP_CLASSES, id_convention=None, method=_assemble_method_qualm_setup(matches=False))
)
def test_check_no_match(cls, args):
    qualms = []
    cls.check(qualms, 0, *args)
    assert qualms == []


IMG_REF_A = initialize_image_reference(1)
IMG_REF_B = initialize_image_reference(2)
IMG_REF_C = initialize_image_reference(3)


@categorize(category="qualms")
@parametrize(
    "qualm_a,args_a,qualm_b,args_b",
    assemble_arguments(
        (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B)),
        (qualms.OutOfRange, (IMG_REF_A,)),
        method=_assemble_method_permutations()
    )
)
def test_comparison_different_types(qualm_a, args_a, qualm_b, args_b):
    qualm_object_a = qualm_a(0, *args_a)
    qualm_object_b = qualm_b(0, *args_b)

    assert (qualm_object_a == qualm_object_b) is False


@categorize(category="qualms")
@parametrize(
    "qualm,args_a,args_b",
    assemble_arguments(
        (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B), (IMG_REF_A, IMG_REF_C)),
        (qualms.OutOfRange, (IMG_REF_A,), (IMG_REF_B,))
    )
)
def test_comparison_false(qualm, args_a, args_b):
    qualm_object_a = qualm(0, *args_a)
    qualm_object_b = qualm(0, *args_b)

    assert (qualm_object_a == qualm_object_b) is False


@categorize(category="qualms")
@parametrize(
    "qualm,args", 
    assemble_arguments(
        (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B)),
        (qualms.OutOfRange, (IMG_REF_A,))
    )
)
def test_comparison_invalid_type(qualm, args):
    qualm_object = qualm(0, *args)
    wrong_type = "STRING IS NOT VALID."

    with pytest.raises(errors.TypeError):
        qualm_object == wrong_type


@categorize(category="qualms")
@parametrize(
    "qualm,args",
    assemble_arguments(
        (qualms.DrawingConfliction, (IMG_REF_A, IMG_REF_B)),
        (qualms.OutOfRange, (IMG_REF_A,))
    )
)
def test_comparison_true(qualm, args):
    qualm_object_a = qualm(0, *args)
    qualm_object_b = qualm(0, *args)

    assert (qualm_object_a == qualm_object_b) is True


@categorize(category="qualms")
@parametrize(
    "qualm_cls,args,expected",
    assemble_arguments(
        (qualms.DrawingConfliction,
         (create_image_reference("1", ""), create_image_reference("2", "")),
         ":D101:4: images with IDs \'1\' and \'2\' overlap with each other"),
        (qualms.OutOfRange,
         (create_image_reference("1", ""),),
         ":D102:3: image with ID \'1\' may be printed outside of canvas boundaries")
    )
)
def test_message(qualm_cls, args, expected):
    qualm = qualm_cls(0, *args)
    assert str(qualm) == expected
