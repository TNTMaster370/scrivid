from __future__ import annotations

from .._utils.sentinel_objects import sentinel
import scrivid.exceptions
from .files import call_close, FileAccess
from .properties import Properties

from pathlib import Path
from typing import TYPE_CHECKING
import weakref

from PIL import Image

if TYPE_CHECKING:
    from typing import Union


_NS = sentinel("_NOT_SPECIFIED")


class ImageFileReference:
    __slots__ = ("__file", "__file_handler")

    def __init__(self, file: Union[str, Path], /):
        if not isinstance(file, Path):
            file = Path(file)

        self.__file = file
        self.__file_handler = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.__file!r}, "
            + ("is_opened" if self.__file_handler is not None else "is_closed")
            + ")"
        )

    @property
    def is_opened(self):
        return self.__file_handler is not None

    def open(self):
        self.__file_handler = Image.open(self.__file)

    def close(self):
        if self.__file_handler is None:
            return
        self.__file_handler.close()
        self.__file_handler = None


class ImageReference:
    __slots__ = ("__file", "__finalizer", "__properties", "__weakref__")

    def __init__(self, file: FileAccess, properties: Properties = _NS, /):
        self.__file = file
        self.__finalizer = weakref.finalize(self, call_close, self.__file)
        self.__properties = properties

    def __repr__(self):
        return f"{self.__class__.__name__}(file={self.__file!r}, properties={self.__properties!r})"

    @property
    def is_opened(self):
        return self.__file.is_opened

    @property
    def layer(self):
        return self.__properties.layer

    @property
    def scale(self):
        return self.__properties.scale

    @property
    def x(self):
        return self.__properties.x

    @property
    def y(self):
        return self.__properties.y

    def open(self):
        # ImageReference is not responsible for opening/closing a file. It's
        # purpose is to hold the data for it. As such, it only calls the 'open'
        # method of its .__file attribute. If the interface is incompatible, it
        # is the responsibility of the FileReference_-like class to manage it.
        self.__file.open()

    def close(self):
        # This 'close' method is automatically called when the object is
        # deleted, but ImageReference is not responsible for what comes out of
        # .__file.close(). Make sure the FileReference_-like class returns
        # early if the file is closed, because this method will not catch it.
        self.__file.close()


def image_reference(
        file: Union[str, Path, FileAccess],
        properties: Union[Properties, _NS] = _NS,
        /, *,
        layer: Union[int, _NS] = _NS,
        scale: Union[int, _NS] = _NS,
        x: Union[int, _NS] = _NS,
        y: Union[int, _NS] = _NS
) -> ImageReference:
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file, Path):
        file = ImageFileReference(file)

    if properties is _NS:
        properties = Properties(layer, scale, x, y)
    else:
        for name, attr in (("layer", layer), ("scale", scale), ("x", x), ("y", y)):
            if attr is not _NS:
                raise scrivid.exceptions.AttributeError(f"Attribute \'{name}\' should not be specified if "
                                                        "\'properties\' is.")

    return ImageReference(file, properties)
