import scrivid.errors
from scrivid import errors, image_reference, ImageReference, Properties, RootAdjustment

from pathlib import Path
from typing import Any, List

import pytest


class AdjustmentSubstitute(RootAdjustment):
    __slots__ = ("state",)

    def __init__(self, ID, activation_time: int):
        super().__init__(ID, activation_time)
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

    def __init__(self, layer=None, scale=None, x=None, y=None):
        self.state: List[Any] = ["INIT"]
        # The type annotation is to prevent issues with type checkers.
        super().__init__(layer=layer, scale=scale, x=x, y=y)
        self.state.append("POST-INIT")

    def __setattr__(self, key, value):
        if hasattr(self, "state"):
            self.state.append((key, value))
        super().__setattr__(key, value)


def test_image_adjustments():
    adj1 = AdjustmentSubstitute(0, 10)
    adj2 = AdjustmentSubstitute(0, 20)

    img_ref = image_reference(0, "")
    img_ref.add_adjustment(adj1)
    img_ref.add_adjustment(adj2)

    assert img_ref.adjustments == {adj1, adj2}


def test_image_adjustments_sorting():
    adj_10 = AdjustmentSubstitute(0, 10)
    adj_20 = AdjustmentSubstitute(0, 20)
    adj_30 = AdjustmentSubstitute(0, 30)

    img_ref = image_reference(0, "some/file")
    img_ref.add_adjustment(adj_30)
    img_ref.add_adjustment(adj_20)
    img_ref.add_adjustment(adj_10)

    assert img_ref.adjustments == {adj_10, adj_20, adj_30}
    # Insertion order does not match sorted order.


def test_image_copy():
    img_ref = ImageReference(0, FileSubstitute(""), PropertiesSubstitute())
    copy_img_ref = img_ref.copy(1)
    deepcopy_img_ref = img_ref.deepcopy(2)

    # The point of these tests is to ensure that the .copy() and .deepcopy()
    # functions are actually making copies of what they need to.
    assert id(img_ref) != id(copy_img_ref)
    assert id(img_ref) != id(deepcopy_img_ref)
    assert id(img_ref.adjustments) != id(deepcopy_img_ref.adjustments)


def test_image_file_management():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(0, file_handler, PropertiesSubstitute())

    img_ref.open()
    img_ref.close()

    assert file_handler.state == ["open", "close"]


def test_image_file_management_weakref():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(0, file_handler, PropertiesSubstitute())

    img_ref.open()
    del img_ref  # The method to close should be called when `i`s
    # reference count hits zero.

    assert file_handler.state == ["open", "close"]


def test_image_function_multi_declare_properties():
    with pytest.raises(errors.AttributeError):
        image_reference(0, "", Properties(layer=0, scale=0, x=0, y=0), x=1, y=1)


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


def test_property_function_return():
    _ = scrivid.properties(layer=1, scale=1, x=1, y=1)  # should raise no error


def test_property_merge():
    a = Properties(layer=1)
    b = Properties(scale=1)

    c = a.merge(b)

    assert c.layer == 1
    assert c.scale == 1


def test_property_merge_confliction():
    a = Properties(x=1)
    b = Properties(x=2, y=2)

    with pytest.raises(scrivid.errors.AttributeError):
        a.merge(b)

    with pytest.raises(scrivid.errors.AttributeError):
        b.merge(a)


def test_property_merge_confliction_not_strict():
    a = Properties(x=1)
    b = Properties(x=2, y=2)

    # Note: when the merge function has the strict flag disabled, it will use
    # the properties from the 'self' caller are favoured in the merging.
    c = a.merge(b, strict=False)
    assert c.x == 1

    d = b.merge(a, strict=False)
    assert d.x == 2


def test_property_merge_invalid_type():
    a = Properties(scale=1)
    b = ImageReference(10, FileSubstitute(""), PropertiesSubstitute())

    with pytest.raises(scrivid.errors.TypeError):
        a.merge(b)


def test_property_merge_ampersand_operator():
    a = Properties(layer=1)
    b = Properties(scale=1)

    c = a & b

    assert c.layer == 1
    assert c.scale == 1


def test_property_merge_ampersand_operator_confliction():
    a = Properties(x=1)
    b = Properties(x=2, y=2)

    with pytest.raises(scrivid.errors.AttributeError):
        a & b

    with pytest.raises(scrivid.errors.AttributeError):
        b & a


def test_property_merge_ampersand_operator_invalid_type():
    a = Properties(scale=1)
    b = ImageReference(10, FileSubstitute(""), PropertiesSubstitute())

    with pytest.raises(scrivid.errors.TypeError):
        a & b
