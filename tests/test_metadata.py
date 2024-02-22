from functions import assemble_arguments
from scrivid import errors, Metadata

import pytest


# ALIAS
parametrize = pytest.mark.parametrize

FILL_VALUE = object()

METADATA_DEFAULTS = {
    "frame_rate": 0,
    "save_location": "",
    "video_name": "",
    "window_size": (0, 0)
}


def _assemble_method_delete(arguments, _):
    argument = arguments[0]
    for key in argument:
        current_values = argument.copy()
        del current_values[key]
        metadata = Metadata(**current_values)
        yield pytest.param(metadata, id=key)


def _assemble_method_fillvalue(arguments, _):
    argument = arguments[0]
    for key in argument:
        current_values = argument.copy()
        current_values[key] = FILL_VALUE
        metadata = Metadata(**current_values)
        yield pytest.param(metadata, id=key)


@parametrize("metadata", assemble_arguments(METADATA_DEFAULTS, method=_assemble_method_delete))
def test_validation_presense(metadata):
    with pytest.raises(errors.AttributeError):
        metadata._validate()


@parametrize("metadata", assemble_arguments(METADATA_DEFAULTS, method=_assemble_method_fillvalue))
def test_validation_type(metadata):
    with pytest.raises(errors.AttributeError):
        metadata._validate()


@parametrize("updated_window_size", [(5, 0), (0, 5)], ids=["width", "height"])
def test_validation_window_size_odd_numbers(updated_window_size):
    metadata = Metadata(frame_rate=0, save_location="", video_name="")
    metadata.window_size = updated_window_size
    with pytest.raises(errors.AttributeError):
        metadata._validate()


def test_window_attributes():
    metadata = Metadata(window_size=(8, 6))
    assert metadata.window_size == (8, 6)
    assert metadata.window_height == 6
    assert metadata.window_width == 8

    metadata.window_size = (10, 8)
    assert metadata.window_size == (10, 8)


def test_window_attributes_exclusion():
    metadata = Metadata()
    assert metadata.window_height is None
    assert metadata.window_width is None
