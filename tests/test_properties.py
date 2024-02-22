from scrivid import errors, ImageReference, properties, VisibilityStatus

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


def test_merge():
    a = properties.Properties(layer=1)
    b = properties.Properties(scale=1)

    c = a.merge(b)

    assert c.layer == 1
    assert c.scale == 1


def test_merge_ampersand_operator():
    a = properties.Properties(layer=1)
    b = properties.Properties(scale=1)

    c = a & b

    assert c.layer == 1
    assert c.scale == 1


def test_merge_confliction():
    a = properties.Properties(x=1)
    b = properties.Properties(x=2, y=2)

    with pytest.raises(errors.ConflictingAttributesError):
        a.merge(b)

    with pytest.raises(errors.ConflictingAttributesError):
        b.merge(a)


def test_merge_confliction_ampersand_operator():
    a = properties.Properties(x=1)
    b = properties.Properties(x=2, y=2)

    with pytest.raises(errors.ConflictingAttributesError):
        a & b

    with pytest.raises(errors.ConflictingAttributesError):
        b & a


def test_merge_missing_attribute():
    a = properties.Properties(x=1)
    b = properties.Properties(x=1)
    del a.x

    with pytest.raises(errors.AttributeError):
        a.merge(b)

    with pytest.raises(errors.AttributeError):
        b.merge(a)


def test_merge_missing_attribute_ampersand_operator():
    a = properties.Properties(x=1)
    b = properties.Properties(x=1)
    del a.x

    with pytest.raises(errors.AttributeError):
        a & b

    with pytest.raises(errors.AttributeError):
        b & a


def test_merge_mode_append():
    a = properties.Properties(visibility=VisibilityStatus.HIDE, x=1)
    b = properties.Properties(visibility=VisibilityStatus.SHOW, x=2)

    c = a.merge(b, mode=properties.MergeMode.APPEND)
    assert c.x == 3
    assert c.visibility is VisibilityStatus.HIDE

    d = b.merge(a, mode=properties.MergeMode.APPEND)
    assert d.visibility is VisibilityStatus.SHOW
    # 'visibility' is not invoked via appending the same way, since adding
    # two enum objects is not possible, so it invokes the replacement
    # behaviour instead. This is why there's a reverse-append option.


def test_merge_mode_replacement():
    a = properties.Properties(x=1)
    b = properties.Properties(x=2, y=2)

    c = a.merge(b, mode=properties.MergeMode.REPLACEMENT)
    assert c.x == 1

    d = b.merge(a, mode=properties.MergeMode.REPLACEMENT)
    assert d.x == 2


def test_merge_mode_reverse_append():
    a = properties.Properties(visibility=VisibilityStatus.HIDE, x=1)
    b = properties.Properties(visibility=VisibilityStatus.SHOW, x=2)

    c = a.merge(b, mode=properties.MergeMode.REVERSE_APPEND)
    assert c.x == 3
    assert c.visibility is VisibilityStatus.SHOW

    d = b.merge(a, mode=properties.MergeMode.REVERSE_APPEND)
    assert d.visibility is VisibilityStatus.HIDE


def test_merge_mode_reverse_replacement():
    a = properties.Properties(x=1)
    b = properties.Properties(x=2, y=2)

    c = a.merge(b, mode=properties.MergeMode.REVERSE_REPLACEMENT)
    assert c.x == 2

    d = b.merge(a, mode=properties.MergeMode.REVERSE_REPLACEMENT)
    assert d.x == 1


def test_merge_mode_reverse_strict_replacement():
    a = properties.Properties(x=1)
    b = properties.Properties(y=2)

    c = a.merge(b, mode=properties.MergeMode.REVERSE_STRICT_REPLACEMENT)
    assert c.x == 1
    assert c.y == 2

    d = b.merge(a, mode=properties.MergeMode.REVERSE_STRICT_REPLACEMENT)
    assert d.x == 1
    assert d.y == 2


def test_merge_mode_reverse_strict_replacement_confliction():
    a = properties.Properties(x=1)
    b = properties.Properties(x=2, y=2)

    with pytest.raises(errors.ConflictingAttributesError):
        a.merge(b, mode=properties.MergeMode.REVERSE_STRICT_REPLACEMENT)

    with pytest.raises(errors.ConflictingAttributesError):
        b.merge(a, mode=properties.MergeMode.REVERSE_STRICT_REPLACEMENT)


def test_merge_invalid_type():
    a = properties.Properties(scale=1)
    b = ImageReference(10, FileSubstitute(""), properties.create())

    with pytest.raises(errors.TypeError):
        a.merge(b)


def test_merge_invalid_type_ampersand_operator():
    a = properties.Properties(scale=1)
    b = ImageReference(10, FileSubstitute(""), properties.create())

    with pytest.raises(errors.TypeError):
        a & b
