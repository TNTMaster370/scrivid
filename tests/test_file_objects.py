from functions import get_current_directory

from scrivid import create_image_reference, define_properties, errors, ImageReference, Properties, RootAdjustment, \
    VisibilityStatus

import pytest


class AdjustmentSubstitute(RootAdjustment):
    __slots__ = ("state",)

    def __init__(self, ID, activation_time: int):
        super().__init__(ID, activation_time)
        self.state = []

    def _enact(self):
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


def test_image_copy():
    img_ref = ImageReference(0, FileSubstitute(""), define_properties())
    copy_img_ref = img_ref.copy(1)
    deepcopy_img_ref = img_ref.deepcopy(2)

    # The point of these tests is to ensure that the .copy() and .deepcopy()
    # functions are actually making copies of what they need to.
    assert id(img_ref) != id(copy_img_ref)
    assert id(img_ref) != id(deepcopy_img_ref)


def test_image_file_management():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(0, file_handler, define_properties())

    img_ref.open()
    img_ref.close()

    assert file_handler.state == ["open", "close"]


def test_image_file_management_weakref():
    file_handler = FileSubstitute("some/file")
    img_ref = ImageReference(0, file_handler, define_properties())

    img_ref.open()
    del img_ref  # The method to close should be called when `i`s
    # reference count hits zero.

    assert file_handler.state == ["open", "close"]


def test_image_function_multi_declare_properties():
    with pytest.raises(errors.AttributeError):
        create_image_reference(0, "", Properties(layer=0, scale=0, x=0, y=0), x=1, y=1)


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


class Test_Properties:
    APPEND = Properties.MERGE_MODE.APPEND
    REVERSE_APPEND = Properties.MERGE_MODE.REVERSE_APPEND
    REVERSE_REPLACEMENT = Properties.MERGE_MODE.REVERSE_REPLACEMENT

    def test_merge(self):
        a = Properties(layer=1)
        b = Properties(scale=1)

        c = a.merge(b)

        assert c.layer == 1
        assert c.scale == 1

    def test_merge_ampersand_operator(self):
        a = Properties(layer=1)
        b = Properties(scale=1)

        c = a & b

        assert c.layer == 1
        assert c.scale == 1

    def test_merge_confliction(self):
        a = Properties(x=1)
        b = Properties(x=2, y=2)

        with pytest.raises(errors.ConflictingAttributesError):
            a.merge(b)

        with pytest.raises(errors.ConflictingAttributesError):
            b.merge(a)

    def test_merge_confliction_ampersand_operator(self):
        a = Properties(x=1)
        b = Properties(x=2, y=2)

        with pytest.raises(errors.ConflictingAttributesError):
            a & b

        with pytest.raises(errors.ConflictingAttributesError):
            b & a

    def test_merge_confliction_not_strict(self):
        a = Properties(x=1)
        b = Properties(x=2, y=2)

        # Note: when the merge function has the strict flag disabled, it will use
        # the properties from the 'self' caller are favoured in the merging.
        c = a.merge(b, strict=False)
        assert c.x == 1

        d = b.merge(a, strict=False)
        assert d.x == 2

    def test_merge_missing_attribute(self):
        a = Properties(x=1)
        b = Properties(x=1)
        del a.x

        with pytest.raises(errors.AttributeError):
            a.merge(b)

        with pytest.raises(errors.AttributeError):
            b.merge(a)

    def test_merge_missing_attribute_ampersand_operator(self):
        a = Properties(x=1)
        b = Properties(x=1)
        del a.x

        with pytest.raises(errors.AttributeError):
            a & b

        with pytest.raises(errors.AttributeError):
            b & a

    def test_merge_mode_append(self):
        a = Properties(visibility=VisibilityStatus.HIDE, x=1)
        b = Properties(visibility=VisibilityStatus.SHOW, x=2)

        c = a.merge(b, mode=self.APPEND, strict=False)
        assert c.x == 3
        assert c.visibility is VisibilityStatus.HIDE

        d = b.merge(a, mode=self.APPEND, strict=False)
        assert d.visibility is VisibilityStatus.SHOW
        # 'visibility' is not invoked via appending the same way, since adding
        # two enum objects is not possible, so it invokes the replacement
        # behaviour instead. This is why there's a reverse-append option.

    def test_merge_mode_reverse_append(self):
        a = Properties(visibility=VisibilityStatus.HIDE, x=1)
        b = Properties(visibility=VisibilityStatus.SHOW, x=2)

        c = a.merge(b, mode=self.REVERSE_APPEND, strict=False)
        assert c.x == 3
        assert c.visibility is VisibilityStatus.SHOW

        d = b.merge(a, mode=self.REVERSE_APPEND, strict=False)
        assert d.visibility is VisibilityStatus.HIDE

    def test_merge_mode_reverse_replacement(self):
        a = Properties(x=1)
        b = Properties(x=2, y=2)

        c = a.merge(b, mode=self.REVERSE_REPLACEMENT, strict=False)
        assert c.x == 2

        d = b.merge(a, mode=self.REVERSE_REPLACEMENT, strict=False)
        assert d.x == 1

    def test_merge_invalid_type(self):
        a = Properties(scale=1)
        b = ImageReference(10, FileSubstitute(""), define_properties())

        with pytest.raises(errors.TypeError):
            a.merge(b)

    def test_merge_invalid_type_ampersand_operator(self):
        a = Properties(scale=1)
        b = ImageReference(10, FileSubstitute(""), define_properties())

        with pytest.raises(errors.TypeError):
            a & b
