from __future__ import annotations

from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Tuple


class _FrameCanvas:
    __slots__ = ("_canvas", "_pixel_canvas", "index")

    def __init__(self, index: int, window_size: Tuple[int, int]):
        self._canvas = Image.new("RGB", window_size, (255, 255, 255))
        self._pixel_canvas = self._canvas.load()
        self.index = index

    def save(self, save_file: Path):
        self._canvas.save(save_file, "PNG")
        self._canvas.close()
        self._canvas = None
        self._pixel_canvas = None

    def set_pixel(self, coordinates: Tuple[int, int], pixel_value: Tuple[int, int, int]):
        # TODO: Implement behaviour for when the coordinates has a negative
        # value, to simply return instead of trying to draw it, since a 
        # negative value draws on the other side, but not vice versa.
        try:
            self._pixel_canvas.__setitem__(coordinates, pixel_value)
        except IndexError:
            pass


class FrameInfo:
    __slots__ = ("canvas", "index", "temp_dir")

    def __init__(self, index: int, temp_dir: Path, window_size: Tuple[int, int]):
        self.canvas = _FrameCanvas(index, window_size)
        self.index = index
        self.temp_dir = temp_dir

    @property
    def save_file(self):
        return self.temp_dir / f"{self.index:06d}.png"
