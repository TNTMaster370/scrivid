from __future__ import annotations

from . import adjustments
from .. import errors
from .._utils.sentinel_objects import sentinel
from .files import call_close, FileAccess
from .properties import Properties
from ._operations import return_not_implemented, should_raise_operator_error

from copy import copy, deepcopy
from pathlib import Path
from typing import TYPE_CHECKING
import weakref

from PIL import Image
from sortedcontainers import SortedSet

if TYPE_CHECKING:
    from .adjustments import RootAdjustment

    from collections.abc import Hashable
    from typing import Optional, Tuple, Union


_NS = sentinel("_NOT_SPECIFIED")


class ImageFileReference:
    __slots__ = ("_file", "_file_handler", "_pixel_handler")

    def __init__(self, file: Union[str, Path], /):
        if not isinstance(file, Path):
            file = Path(file)

        self._file = file
        self._file_handler = None
        self._pixel_handler = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self._file!r}, "
            + ("is_opened" if self._file_handler is not None else "is_closed")
            + ")"
        )

    @property
    def is_opened(self):
        return self._file_handler is not None

    def get_image_height(self):
        if not self.is_opened:
            return None
        else:
            return self._file_handler.height

    def get_image_width(self):
        if not self.is_opened:
            return None
        else:
            return self._file_handler.width

    def get_pixel_value(self, coordinates: Tuple[int, int]):
        if not self.is_opened:
            return None
        else:
            return self._pixel_handler.__getitem__(coordinates)

    def open(self):
        if self._file_handler is not None:
            return
        self._file_handler = Image.open(self._file)
        self._pixel_handler = self._file_handler.load()

    def close(self):
        if self._file_handler is None:
            return
        self._file_handler.close()
        self._file_handler = None
        self._pixel_handler = None


class ImageReference:
    __slots__ = ("_adjustments", "_file", "_finalizer", "_ID", "_properties", "__weakref__")

    _adjustments: SortedSet[RootAdjustment]
    _file: FileAccess
    _finalizer: weakref.finalize
    _ID: Hashable
    _properties: Properties

    def __init__(self, ID: Hashable, file: FileAccess, properties: Properties = _NS, /):
        self._adjustments = SortedSet()
        self._file = file
        self._finalizer = weakref.finalize(self, call_close, self._file)
        self._ID = ID
        self._properties = properties

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(adjustments={self._adjustments!r}, file={self._file!r}, id={self._ID!r}, "
            f"properties={self._properties!r})"
        )

    def __hash__(self):
        return hash(self._ID)

    def __lshift__(self, other):
        """ self << other """
        if not isinstance(other, adjustments.RootAdjustment):
            raise errors.TypeError(f"Expected types RootAdjustment, got type {other.__name__}")
        self.add_adjustment(other)

    """ other << self """
    __rlshift__ = should_raise_operator_error(correct="<<", reverse=">>")

    """ self >> other """
    __rshift__ = return_not_implemented()  # This function does not handle the
    # error that should be raised for incorrect syntax, because doing so in the
    # forward function would be too eager. If someone inherits from
    # RootAdjustment and wants this syntax to work, we should give it a chance
    # to invoke the reverse method.

    def __rrshift__(self, other):
        """ other >> self """
        if not isinstance(other, adjustments.RootAdjustment):
            raise errors.TypeError(f"Expected types RootAdjustment, got type {other.__name__}")
        self.add_adjustment(other)

    @property
    def adjustments(self):
        return self._adjustments

    # I'm allowing both lowercase and uppercase 'ID' access, since I'm
    # primarily using the uppercase equivalent to prevent name shadowing.
    @property
    def id(self):
        return self._ID

    @property
    def ID(self):
        return self._ID

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

    def copy(self, new_ID: Hashable):
        c = copy(self)
        c._ID = new_ID
        return c

    def deepcopy(self, new_ID: Hashable, memo: Optional[dict] = None):
        if memo is None:
            memo = {}
        dc = deepcopy(self, memo)
        dc._ID = new_ID
        return dc

    def add_adjustment(self, new_adjustment: RootAdjustment):
        self._adjustments.add(new_adjustment)

    def get_image_height(self):
        self._file: ImageFileReference
        return self._file.get_image_height()

    def get_image_width(self):
        self._file: ImageFileReference
        return self._file.get_image_width()

    def get_pixel_value(self, coordinates: Tuple[int, int]):
        self._file: ImageFileReference
        return self._file.get_pixel_value(coordinates)

    def open(self):
        # ImageReference is not responsible for opening/closing a file. It's
        # purpose is to hold the data for it. As such, it only calls the 'open'
        # method of its ._file attribute.
        self._file.open()

    def close(self):
        # This 'close' method is automatically called when the object is
        # deleted, but ImageReference is not responsible for what comes out of
        # ._file.close(). Make sure the FileAccess-like class returns early if
        # the file is closed, because this method will not catch it.
        self._file.close()


def image_reference(
        ID: Hashable,
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

    return ImageReference(ID, file, properties)
