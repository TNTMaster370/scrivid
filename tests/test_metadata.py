from scrivid import errors, Metadata

import pytest


def test_metadata_fps_confliction():
    with pytest.raises(errors.AttributeError):
        Metadata(fps=24, frame_rate=30)  # These two attributes are the same
        # attribute in the end, so both shouldn't be used in the first place,
        # but it's allowed if the value is identical for both.


def test_metadata_window_attributes():
    metadata = Metadata(window_size=(8, 6))
    assert metadata.window_size == (8, 6)
    assert metadata.window_height == 6
    assert metadata.window_width == 8

    metadata.window_size = (10, 8)
    assert metadata.window_size == (10, 8)
