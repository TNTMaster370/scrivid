from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable, Union


@runtime_checkable
class FileAccess(Protocol):
    """
    FileAccess classes must have two methods: open() and close(). The signature
    of its __init__ method must have one positional-only argument: 'file'.
    """
    def __init__(self, file: Union[str, Path], /): ...
    def open(self): ...
    def close(self): ...


def call_close(file: FileAccess):
    file.close()


class FileReference:
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

    def open(self):
        self.__file_handler = self.__file.open()

    def close(self):
        if self.__file_handler is None:
            return
        self.__file_handler.close()
        self.__file_handler = None
