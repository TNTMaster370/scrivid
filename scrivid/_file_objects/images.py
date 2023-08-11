from __future__ import annotations

from .files import call_close, FileAccess, FileReference

from pathlib import Path
from typing import Union
import weakref


class ImageReference:
    __slots__ = ("__file", "__finalizer", "__weakref__")

    def __init__(self, file: FileAccess, /):
        self.__file = file
        self.__finalizer = weakref.finalize(self, call_close, self.__file)

    def __repr__(self):
        return f"{self.__class__.__name__}(file={self.__file!r})"

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


def image_reference(file: Union[str, Path, FileAccess], /) -> ImageReference:
    if isinstance(file, FileAccess):
        return ImageReference(file)
    elif isinstance(file, Path):
        return ImageReference(FileReference(file))
    elif isinstance(file, str):
        return ImageReference(FileReference(Path(file)))
