from __future__ import annotations

from ._utils.sentinel_objects import sentinel

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, Union


_NOT_SPECIFIED = sentinel("_NOT_SPECIFIED")
_SPECIFIED = not _NOT_SPECIFIED


class Metadata:
    __slots__ = ("_window_size", "frame_rate", "save_location", "video_name")

    _window_size: Tuple[int, int]

    def __init__(
        self, *, fps: Union[int, _NOT_SPECIFIED] = _NOT_SPECIFIED,
        frame_rate: Union[int, _NOT_SPECIFIED] = _NOT_SPECIFIED,
        save_location: Union[str, Path, _NOT_SPECIFIED] = _NOT_SPECIFIED,
        video_name: Union[str, _NOT_SPECIFIED] = _NOT_SPECIFIED,
        window_size: Union[Tuple[int, int], _NOT_SPECIFIED] = _NOT_SPECIFIED
    ):
        """
        Metadata stores all of the attributes for a Scrivid-generated video.
        The attributes are not required to be specified on construction, but
        four attributes must be specified before the Metadata is passed into
        Scrivid to be compiled into a video.

        The four required attributes are frame_rate, save_location, video_name,
        window_size.

        :param fps: Shorthand attribute for frame_rate.
        :param frame_rate: The frame rate of the video.
        :param save_location: The path of the location where the file should be
            saved. Recommended to be a pathlib.Path object.
        :param video_name: The final name of the video file that's to be
            generated.
        :param window_size: A tuple of (width, height) for the dimensions of
            the video.
        """
        if _NOT_SPECIFIED not in (fps, frame_rate) and fps != frame_rate:
            from . import exceptions
            raise exceptions.AttributeError("Conflicting attributes: \'fps\' and \'frame_rate\'")
        elif fps is _SPECIFIED:
            self.frame_rate = fps
        elif frame_rate is _SPECIFIED:
            self.frame_rate = frame_rate

        if isinstance(save_location, str):
            save_location = Path(save_location)
        self.save_location = save_location

        self._window_size = window_size
        self.video_name = video_name

    @property
    def window_height(self):
        if self._window_size is _NOT_SPECIFIED:
            return None
        else:
            return self._window_size[1]

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, new_value: Tuple[int, int]):
        self._window_size = new_value

    @property
    def window_width(self):
        if self._window_size is _NOT_SPECIFIED:
            return None
        else:
            return self._window_size[0]
