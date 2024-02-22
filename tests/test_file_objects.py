from functions import get_current_directory

from scrivid import create_image_reference, errors, ImageReference, properties

import pytest


class FileSubstitute:
    def __init__(self, file):
        self.state = []
        self._file = file

    @property
    def is_opened(self):
        return False  # This property is included to prevent type checking
        # issues.

    def open(self):
        self.state.append("open")

    def close(self):
        self.state.append("close")


def test_image_copy():
    img_ref = ImageReference(0, FileSubstitute(""), properties.create())
    copy_img_ref = img_ref.copy(1)
    deepcopy_img_ref = img_ref.deepcopy(2)

    # The point of these tests is to ensure that the .copy() and .deepcopy()
    # functions are actually making copies of what they need to.
    assert id(img_ref) != id(copy_img_ref)
    assert id(img_ref) != id(deepcopy_img_ref)


def test_image_file_management():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(0, file_handler, properties.create())

    img_ref.open()
    img_ref.close()

    assert file_handler.state == ["open", "close"]


def test_image_file_management_weakref():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(0, file_handler, properties.create())

    img_ref.open()
    del img_ref  # The method to close should be called when `i`s
    # reference count hits zero.

    assert file_handler.state == ["open", "close"]


def test_image_function_multi_declare_properties():
    with pytest.raises(errors.AttributeError):
        create_image_reference(0, "", properties.Properties(layer=0, scale=0, x=0, y=0), x=1, y=1)


def test_image_open_no_errors():
    image_directory = get_current_directory() / "images/img1.png"
    img_ref = create_image_reference(0, image_directory)
    img_ref.open()  # This call to .open() should not raise any exceptions.


def test_image_open_property():
    image_directory = get_current_directory() / "images/img1.png"
    img_ref = create_image_reference(0, image_directory)

    assert img_ref.is_opened is False

    img_ref.open()  # If `test_image_open_no_errors` fails, this ends up
    # failing by extension.
    assert img_ref.is_opened is True

    img_ref.close()
    assert img_ref.is_opened is False
