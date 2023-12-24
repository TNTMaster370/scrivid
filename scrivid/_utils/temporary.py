from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Callable, TypeVar

    T = TypeVar("T")
    CLEANUP_CALLABLE = Callable[[T], None]


class TemporaryAttribute:
    __slots__ = ("_cleanup_function", "value")

    _cleanup_function: CLEANUP_CALLABLE
    value: T

    def __init__(
            self,
            value: T = None,
            *,
            cleanup: CLEANUP_CALLABLE = (lambda _: None)
    ):
        self._cleanup_function = cleanup
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.destroy()

    def destroy(self):
        self._cleanup_function(self.value)
        self.value = None


class TemporaryDirectory:
    def __init__(self, dir: Path):
        self.dir = dir

    def __enter__(self):
        os.mkdir(self.dir)
        return self

    def __exit__(self, *_):
        shutil.rmtree(self.dir)
