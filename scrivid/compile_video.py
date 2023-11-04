from __future__ import annotations

from ._file_objects import VisibilityStatus
from ._file_objects.images import ImageReference
from ._motion_tree import nodes, parse
from ._utils import ticking

from copy import deepcopy
import os
import shutil
from typing import NamedTuple, TYPE_CHECKING

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


class _FrameInformation(NamedTuple):
    index: int
    occurrences: int


class _TemporaryDirectory:
    def __init__(self, folder_location: Path):
        self.dir = folder_location / ".scrivid-cache"

    def __enter__(self):
        os.mkdir(self.dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.dir)


def _create_frame(
        index: int, 
        occurrences: int, 
        references: Sequence[REFERENCES], 
        window_size: Tuple[int, int], 
        image_directory: Path
):
    frame = _FrameCanvas(window_size)
    references_access = deepcopy(references)  # Avoid modifying the original
    # objects.

    for obj in references_access:
        while obj.adjustments:
            adj = obj.adjustments.pop(0)

            if adj.activation_time > index:
                break

            change = adj._enact().merge(obj._properties, strict=False)
            obj._properties = change

        if obj.visibility is VisibilityStatus.HIDE:
            continue

        if not obj.is_opened:
            obj.open()

        obj_x = obj.x
        obj_y = obj.y

        for x, y in ticking(
                range(obj_x, obj_x + obj.get_image_width()),
                range(obj_y, obj_y + obj.get_image_height())
        ):
            frame.update_pixel((x, y), obj.get_pixel_value((x - obj_x, y - obj_y)))

    for additional_index in range(occurrences):
        frame.save(image_directory / f"{index + additional_index}.png", "PNG")


def _generate_frames(motion_tree: MotionTree):
    frames = []
    index = 0

    for node in motion_tree.body:
        type_ = type(node)
        if type_ is nodes.Start:
            frames.append(_FrameInformation(0, 1))
        elif type_ in (nodes.HideImage, nodes.ShowImage):  # nodes.Start
            if index == frames[-1].index:
                continue
            frames.append(_FrameInformation(index, 1))
        elif type_ is nodes.Continue:
            frame = frames[-1]
            frames[-1] = _FrameInformation(frame.index, frame.occurrences + node.length)
            del frame
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
        video_length, frames = _generate_frames(motion_tree)

        for frame_information in frames:
            _create_frame(*frame_information, references, metadata.window_size, temp_dir.dir)

        _stitch_video(temp_dir.dir, video_length, metadata)
