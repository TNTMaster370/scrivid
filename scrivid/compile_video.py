from __future__ import annotations

from ._file_objects import VisibilityStatus
from ._file_objects.adjustments import HideAdjustment, ShowAdjustment
from ._file_objects.images import ImageReference
from ._motion_tree import nodes, parse
from ._utils import ticking

import os
import shutil
from typing import TYPE_CHECKING

from PIL import Image

from moviepy.editor import ImageClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

if TYPE_CHECKING:
    from .metadata import Metadata

    from collections.abc import Sequence
    from pathlib import Path
    from typing import Tuple

    MotionTree = nodes.MotionTree
    REFERENCES = ImageReference


def _determine_visibility_status(adjustments, frame_index):
    if not adjustments:
        return VisibilityStatus.SHOW

    status = VisibilityStatus.HIDE

    for adj in adjustments:
        if type(adj) not in (HideAdjustment, ShowAdjustment):
            continue

        time = adj.activation_time
        if time > frame_index:
            break

        if status is not VisibilityStatus.HIDE and type(adj) is HideAdjustment:
            status = VisibilityStatus.HIDE
        elif status is not VisibilityStatus.SHOW and type(adj) is ShowAdjustment:
            status = VisibilityStatus.SHOW

    return status


class _Frame:
    __slots__ = ("_frame", "_references_access", "_save_location", "_size", "index", "occurrences")

    def __init__(
            self,
            index: int,
            window_size: Tuple[int, int],
            save_location: Path,
            references_access: Sequence[REFERENCES]
    ):
        self._frame = None
        self._references_access = references_access
        self._save_location = save_location
        self._size = window_size
        self.index = index
        self.occurrences = 0

    def __repr__(self):
        return f"{self.__class__.__name__}(index={self.index})"

    def draw_frame(self):
        if self._frame:
            self.index += 1
            self.save_frame()
            return

        self._frame = _FrameCanvas(self._size)

        for obj in self._references_access:
            if _determine_visibility_status(obj.adjustments, self.index) is VisibilityStatus.HIDE:
                continue

            if not obj.is_opened:
                obj.open()

            obj_x = obj.x
            obj_y = obj.y

            for x, y in ticking(
                    range(obj_x, obj_x + obj.get_image_width()),
                    range(obj_y, obj_y + obj.get_image_height())
            ):
                self._frame.update_pixel((x, y), obj.get_pixel_value((x - obj_x, y - obj_y)))

        self.save_frame()

    def save_frame(self):
        self._frame.save(self._save_location / f"{self.index}.png", "PNG")


class _FrameCanvas:
    __slots__ = ("_canvas", "_pixel_canvas")

    def __init__(self, size: Tuple[int, int]):
        self._canvas = Image.new("RGB", size, (255, 255, 255))
        self._pixel_canvas = self._canvas.load()

    def save(self, filename: Path, format_: str):
        self._canvas.save(filename, format_)

    def update_pixel(self, coordinates: Tuple[int, int], new_pixel_value: Tuple[int, int, int]):
        try:
            self._pixel_canvas.__setitem__(coordinates, new_pixel_value)
        except IndexError:
            pass


class _TemporaryDirectory:
    def __init__(self, folder_location: Path):
        self.dir = folder_location / ".scrivid-cache"

    def __enter__(self):
        os.mkdir(self.dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.dir)


def _generate_frame(motion_tree: MotionTree, references: Sequence[REFERENCES], metadata: Metadata, save_directory):
    # frame = _Frame(index, metadata.window_size, metadata.save_location, references)
    frames = []
    index = 0

    for node in motion_tree.body:
        type_ = type(node)
        if type_ is nodes.Start:
            frames.append(_Frame(0, metadata.window_size, save_directory, references))
        elif type_ in (nodes.HideImage, nodes.ShowImage):
            if index == frames[-1].index:
                continue
            frames.append(_Frame(index, metadata.window_size, save_directory, references))
        elif type_ is nodes.Continue:
            frames[-1].occurrences += node.length
            index += node.length
        elif type_ is nodes.End:
            break

    return index, frames


def _stitch_video(temporary_directory, video_length, metadata):
    clips = [(ImageClip(f"{temporary_directory}\\{m}.png")
              .set_duration(1 / metadata.frame_rate))
             for m in range(video_length)]

    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile(f"{metadata.save_location}\\{metadata.video_name}.mp4", fps=metadata.frame_rate)


def compile_video(references: Sequence[REFERENCES], metadata: Metadata):
    """
    Converts the references into a compiled video.

    :param references: A list of instances of ImageReference's.
    :param metadata: An instance of Metadata that stores the attributes
        of the video.
    """
    motion_tree = parse(references)

    with _TemporaryDirectory(metadata.save_location) as temp_dir:
        video_length, frames = _generate_frame(motion_tree, references, metadata, temp_dir.dir)

        for frame in frames:
            for _ in range(frame.occurrences):
                frame.draw_frame()

        _stitch_video(temp_dir.dir, video_length, metadata)
