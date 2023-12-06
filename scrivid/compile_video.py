from __future__ import annotations

from ._file_objects import VisibilityStatus
from ._file_objects.adjustments import MoveAdjustment
from ._file_objects.images import ImageReference
from ._file_objects.properties import Properties
from ._separating_instructions import separate_instructions
from ._motion_tree import nodes, parse
from ._utils import ticking
from ._video_stitching import stitch_video

from copy import deepcopy
import os
import shutil
from typing import NamedTuple, TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from ._file_objects.adjustments import RootAdjustment
    from ._separating_instructions import SeparatedInstructions
    from .metadata import Metadata

    from collections.abc import Sequence
    from pathlib import Path
    from typing import Union, Tuple

    INSTRUCTIONS = Union[ImageReference, RootAdjustment]
    MotionTree = nodes.MotionTree


class _FrameCanvas:
    __slots__ = ("_canvas", "_pixel_canvas")

    def __init__(self, size: Tuple[int, int]):
        self._canvas = Image.new("RGB", size, (255, 255, 255))
        self._pixel_canvas = self._canvas.load()

    def save(self, filename: Path, format_: str):
        self._canvas.save(filename, format_)

    def update_pixel(
            self,
            coordinates: Tuple[int, int],
            new_pixel_value: Tuple[int, int, int]
    ):
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

    def __exit__(self, *_):
        shutil.rmtree(self.dir)


def _invoke_adjustment_duration(index: int, adj: RootAdjustment):
    # Assume that the `adj` has a 'duration' attribute.
    duration = index - adj.activation_time
    if duration > adj.duration:
        return adj.duration
    else:
        return duration


def _create_frame(
        index: int, 
        occurrences: int, 
        instructions: SeparatedInstructions, 
        window_size: Tuple[int, int], 
        image_directory: Path
):
    frame = _FrameCanvas(window_size)
    instructions_access = deepcopy(instructions)  # Avoid modifying the
    # original objects.
    merge_settings = {"mode": Properties.MERGE_MODE.REVERSE_APPEND}

    for ID, obj in instructions_access.references.items():
        try:
            relevant_adjustments = instructions_access.adjustments[ID]
        except KeyError:
            relevant_adjustments = None

        while relevant_adjustments:
            adj = relevant_adjustments.pop(0)

            if adj.activation_time > index:
                break

            args = ()
            if type(adj) is MoveAdjustment:
                args = (_invoke_adjustment_duration(index, adj),)

            obj._properties = obj._properties.merge(
                adj._enact(*args),
                **merge_settings
            )

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
            frame.update_pixel(
                (x, y),
                obj.get_pixel_value((x - obj_x, y - obj_y))
            )

    for additional_index in range(occurrences):
        frame.save(
            image_directory / f"{index + additional_index:06d}.png",
            "PNG"
        )


def _generate_frames(motion_tree: MotionTree):
    frames = []
    index = 0

    for node in motion_tree.body:
        type_ = type(node)
        if type_ is nodes.Start:
            frames.append(_FrameInformation(0, 1))
        elif type_ in (nodes.HideImage, nodes.MoveImage, nodes.ShowImage):
            if index == frames[-1].index:
                continue
            frames.append(_FrameInformation(index, 1))
        elif type_ is nodes.InvokePrevious:
            for _ in range(node.length):
                frames.append(_FrameInformation(index, 1))
                index += 1
        elif type_ is nodes.Continue:
            frame = frames[-1]
            frames[-1] = _FrameInformation(
                frame.index,
                frame.occurrences + node.length
            )
            del frame
            index += node.length
        elif type_ is nodes.End:
            break

    return frames


def compile_video(instructions: Sequence[INSTRUCTIONS], metadata: Metadata):
    """
    Converts the objects, taken as instructions, into a compiled video.

    :param instructions: A list of instances of ImageReference's, and/or a 
        class of the Adjustment hierarchy.
    :param metadata: An instance of Metadata that stores the attributes
        of the video.
    """
    separated_instructions = separate_instructions(instructions)
    motion_tree = parse(separated_instructions)

    with _TemporaryDirectory(metadata.save_location) as temp_dir:
        frames = _generate_frames(motion_tree)

        for frame_information in frames:
            _create_frame(
                *frame_information,
                separated_instructions,
                metadata.window_size,
                temp_dir.dir
            )

        stitch_video(temp_dir.dir, metadata)
