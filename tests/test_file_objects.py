from scrivid import errors, image_reference, ImageReference, Properties, RootAdjustment

from pathlib import Path
from typing import Any, List

import pytest


class AdjustmentSubstitute(RootAdjustment):
    __slots__ = ("state",)

    def __init__(self, activation_time: int):
        super().__init__(activation_time)
        self.state = []

    def utilize(self, reference):
        self.state.append("utilize")


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


def get_current_directory():
    return Path(".").absolute()


class PropertiesSubstitute(Properties):
    __slots__ = ("state",)

    def __init__(self, layer, scale, x, y):
        self.state: List[Any] = ["INIT"]
        # The type annotation is to prevent issues with type checkers.
        super().__init__(layer, scale, x, y)
        self.state.append("POST-INIT")

    def __setattr__(self, key, value):
        if hasattr(self, "state"):
            self.state.append((key, value))
        super().__setattr__(key, value)


def test_image_adjustments():
    adj1 = AdjustmentSubstitute(10)
    adj2 = AdjustmentSubstitute(20)

    img_ref = image_reference(0, "")
    img_ref.add_adjustment(adj1)
    img_ref.add_adjustment(adj2)

    assert img_ref.adjustments == {adj1, adj2}


def test_image_adjustments_shift_operator():
    adj1 = AdjustmentSubstitute(1)
    adj2 = AdjustmentSubstitute(2)
    adj3 = AdjustmentSubstitute(3)

    img_ref = image_reference(0, "")

    adj1 >> img_ref  # Should raise no error.
    assert img_ref.adjustments == {adj1}

    img_ref << adj2  # Should raise no error.
    assert img_ref.adjustments == {adj1, adj2}

    with pytest.raises(errors.OperatorError):
        adj3 << img_ref

    with pytest.raises(errors.OperatorError):
        img_ref >> adj3


def test_image_adjustments_sorting():
    adj_10 = AdjustmentSubstitute(10)
    adj_20 = AdjustmentSubstitute(20)
    adj_30 = AdjustmentSubstitute(30)

    img_ref = image_reference(0, "some/file")
    img_ref.add_adjustment(adj_30)
    img_ref.add_adjustment(adj_20)
    img_ref.add_adjustment(adj_10)

    assert img_ref.adjustments == {adj_10, adj_20, adj_30}
    # Insertion order does not match sorted order.


def test_image_copy():
    img_ref = ImageReference(0, FileSubstitute(""))
    copy_img_ref = img_ref.copy(1)
    deepcopy_img_ref = img_ref.deepcopy(2)

    # The point of these tests is to ensure that the .copy() and .deepcopy()
    # functions are actually making copies of what they need to.
    assert id(img_ref) != id(copy_img_ref)
    assert id(img_ref) != id(deepcopy_img_ref)
    assert id(img_ref.adjustments) != id(deepcopy_img_ref.adjustments)


def test_image_file_management():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(0, file_handler)

    img_ref.open()
    img_ref.close()

    assert file_handler.state == ["open", "close"]


def test_image_file_management_weakref():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(0, file_handler)

    img_ref.open()
    del img_ref  # The method to close should be called when `i`s
    # reference count hits zero.

    assert file_handler.state == ["open", "close"]


def test_image_function_multi_declare_properties():
    with pytest.raises(errors.AttributeError):
        image_reference(0, "", Properties(0, 0, 0, 0), x=1, y=1)


def test_image_open_no_errors():
    image_directory = get_current_directory() / "tests/images/img1.png"
    img_ref = image_reference(0, image_directory)
    img_ref.open()  # This call to .open() should not raise any exceptions.


def test_image_open_property():
    image_directory = get_current_directory() / "tests/images/img1.png"
    img_ref = image_reference(0, image_directory)

    assert img_ref.is_opened is False

    img_ref.open()  # If `test_image_open_no_errors` fails, this ends up
    # failing by extension.
    assert img_ref.is_opened is True

    img_ref.close()
    assert img_ref.is_opened is False


def test_image_property_attributes():
    properties = PropertiesSubstitute(1, 2, 3, 4)
    image_reference(0, "", properties)
    assert properties.state == ["INIT", ("layer", 1), ("scale", 2), ("x", 3), ("y", 4), "POST-INIT"]
