from scrivid import errors, Metadata

import pytest


# ALIAS
parametrize = pytest.mark.parametrize

METADATA_DEFAULTS = {
    "frame_rate": 0,
    "save_location": "",
    "video_name": "",
    "window_size": (0, 0)
}


def assemble_metadata_args(default_values, *, delete=False, fill_value=None):
    arguments = []

    for key in default_values:
        current_values = default_values.copy()
        if delete:
            del current_values[key]
        else:
            current_values[key] = fill_value

        metadata = Metadata(**current_values)
        arguments.append(pytest.param(metadata, id=key))

    return arguments


@parametrize("metadata", assemble_metadata_args(METADATA_DEFAULTS, delete=True))
def test_validation_presense(metadata):
    with pytest.raises(errors.AttributeError):
        metadata._validate()


@parametrize("metadata", assemble_metadata_args(METADATA_DEFAULTS, fill_value=False))
def test_validation_type(metadata):
    with pytest.raises(errors.AttributeError):
        metadata._validate()


@parametrize("updated_window_size", [
    pytest.param((5, 0), id="width"),
    pytest.param((0, 5), id="height")
])
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
