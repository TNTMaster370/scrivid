from __future__ import annotations

from . import adjustments
from .. import errors
from .._utils.sentinel_objects import sentinel
from .files import call_close, FileAccess
from .properties import Properties
from ._operations import return_not_implemented, should_raise_operator_error
from ._status import Status

from pathlib import Path
from typing import TYPE_CHECKING
import weakref

from PIL import Image

if TYPE_CHECKING:
    from .adjustments import RootAdjustment

    from typing import Union


_NS = sentinel("_NOT_SPECIFIED")


class ImageFileReference:
    __slots__ = ("_file", "_file_handler")

    def __init__(self, file: Union[str, Path], /):
        if not isinstance(file, Path):
            file = Path(file)

        self._file = file
        self._file_handler = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self._file!r}, "
            + ("is_opened" if self._file_handler is not None else "is_closed")
            + ")"
        )

    @property
    def is_opened(self):
        return self._file_handler is not None

    def open(self):
        self._file_handler = Image.open(self._file)

    def close(self):
        if self._file_handler is None:
            return
        self._file_handler.close()
        self._file_handler = None


class ImageReference:
    __slots__ = ("_adjustments", "_file", "_finalizer", "_properties", "_status", "__weakref__")

    def __init__(self, file: FileAccess, properties: Properties = _NS, /):
        self._adjustments = set()
        self._file = file
        self._finalizer = weakref.finalize(self, call_close, self._file)
        self._properties = properties
        self._status = Status.UNKNOWN

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(adjustments={self._adjustments!r}, file={self._file!r}, "
            f"properties={self._properties!r})"
        )

    def __lshift__(self, other):
        """ self << other """
        if not isinstance(other, adjustments.RootAdjustment):
            raise errors.TypeError(f"Expected types RootAdjustment, got type {other.__name__}")
        self.add_adjustment(other)

    """ self << other """
    __rlshift__ = should_raise_operator_error(correct="<<", reverse=">>")

    """ self >> other """
    __rshift__ = return_not_implemented()

    def __rrshift__(self, other):
        """ self >> other """
        if not isinstance(other, adjustments.RootAdjustment):
            raise errors.TypeError(f"Expected types RootAdjustment, got type {other.__name__}")
        self.add_adjustment(other)

    @property
    def adjustments(self):
        return self._adjustments

    @property
    def is_opened(self):
        return self._file.is_opened

    @property
    def layer(self):
        return self._properties.layer

    @property
    def scale(self):
        return self._properties.scale

    @property
    def x(self):
        return self._properties.x

    @property
    def y(self):
        return self._properties.y

    def add_adjustment(self, new_adjustment: RootAdjustment):
        self._adjustments.add(new_adjustment)

    def open(self):
        # ImageReference is not responsible for opening/closing a file. It's
        # purpose is to hold the data for it. As such, it only calls the 'open'
        # method of its ._file attribute. If the interface is incompatible, it
        # is the responsibility of the FileAccess-like class to manage it.
        self._file.open()

    def close(self):
        # This 'close' method is automatically called when the object is
        # deleted, but ImageReference is not responsible for what comes out of
        # ._file.close(). Make sure the FileAccess-like class returns early if
        # the file is closed, because this method will not catch it.
        self._file.close()


def image_reference(
        file: Union[str, Path, FileAccess],
        properties: Union[Properties, _NS] = _NS,
        /, *,
        layer: Union[int, _NS] = _NS,
        scale: Union[int, _NS] = _NS,
        x: Union[int, _NS] = _NS,
        y: Union[int, _NS] = _NS
) -> ImageReference:
    # ...
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file, Path):
        file = ImageFileReference(file)

    if properties is _NS:
        properties = Properties(layer, scale, x, y)
    else:
        for name, attr in (("layer", layer), ("scale", scale), ("x", x), ("y", y)):
            if attr is not _NS:
                raise errors.AttributeError(f"Attribute \'{name}\' should not be specified if \'properties\' is.")

    return ImageReference(file, properties)
