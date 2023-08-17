from scrivid import errors, image_reference, ImageReference, Properties

from pathlib import Path

import pytest


def get_current_directory():
    return Path(".").absolute()


class FileSubstitute:
    def __init__(self, file):
        self.state = []
        self.__file = file

    @property
    def is_opened(self):
        return False  # This property is included to prevent type checking
        # issues.

    def open(self):
        self.state.append("open")

    def close(self):
        self.state.append("close")


def test_image_file_management():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(file_handler)

    img_ref.open()
    img_ref.close()

    assert file_handler.state == ["open", "close"]


def test_image_file_management_weakref():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(file_handler)

    img_ref.open()
    del img_ref  # The method to close should be called when `i`s
    # reference count hits zero.

    assert file_handler.state == ["open", "close"]


def test_image_function_multi_declare_properties():
    with pytest.raises(errors.AttributeError):
        image_reference("", Properties(0, 0, 0, 0), x=1, y=1)


def test_image_open_no_errors():
    image_directory = get_current_directory() / "tests/images/img1.png"
    img_ref = image_reference(image_directory)
    img_ref.open()  # This call to .open() should not raise any exceptions.


def test_image_open_property():
    image_directory = get_current_directory() / "tests/images/img1.png"
    img_ref = image_reference(image_directory)

    assert img_ref.is_opened is False

    img_ref.open()  # If `test_image_open_no_errors` fails, this ends up
    # failing by extension.
    assert img_ref.is_opened is True

    img_ref.close()
    assert img_ref.is_opened is False
