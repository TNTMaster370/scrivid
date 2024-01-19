from scrivid import errors, Metadata

import pytest


# ALIAS
parametrize = pytest.mark.parametrize


@parametrize("metadata", [
    Metadata(save_location="", video_name="", window_size=(0, 0)),
    Metadata(frame_rate=0, video_name="", window_size=(0, 0)),
    Metadata(frame_rate=0, save_location="", window_size=(0, 0)),
    Metadata(frame_rate=0, save_location="", video_name="")
])
def test_validation_presense(metadata):
    with pytest.raises(errors.AttributeError):
        metadata._validate()


@parametrize("metadata", [
    Metadata(frame_rate=False, save_location="", video_name="", window_size=(0, 0)),
    Metadata(frame_rate=0, save_location=False, video_name="", window_size=(0, 0)),
    Metadata(frame_rate=0, save_location="", video_name=False, window_size=(0, 0)),
    Metadata(frame_rate=0, save_location="", video_name="", window_size=False)
])
def test_validation_type(metadata):
    with pytest.raises(errors.AttributeError):
        metadata._validate()


@parametrize("updated_window_size", [(5, 0), (0, 5)])
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
