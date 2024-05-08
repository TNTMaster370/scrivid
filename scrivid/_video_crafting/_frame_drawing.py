from __future__ import annotations

from .. import adjustments, motion_tree, properties
from .._utils import TemporaryAttribute

from copy import deepcopy
import itertools
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from ..abc import Adjustment
    from .._separating_instructions import SeparatedInstructions

    from pathlib import Path
    from typing import List, Tuple

    MotionTree = motion_tree.MotionTree


def _call_close(value):
    value.close()


class _FrameCanvas:
    __slots__ = ("_canvas", "_pixel_canvas", "index", "references", "temporary_directory", "window_size")

    def __init__(self, index: int, temporary_directory: Path, window_size: Tuple[int, int]):
        self._canvas = Image.new("RGB", window_size, (255, 255, 255))
        self._pixel_canvas = self._canvas.load()
        self.index = index
        self.references = {}
        self.temporary_directory = temporary_directory
        self.window_size = window_size

    def save(self):
        self._canvas.save(self.temporary_directory / f"{self.index:06d}.png", "PNG")
        self._canvas.close()
        self._canvas = None
        self._pixel_canvas = None

    def update_pixel(
            self,
            coordinates: Tuple[int, int],
            new_pixel_value: Tuple[int, int, int]
    ):
        # if coordinates[0] < 0 or coordinates[1] < 0:
        #     return

        try:
            self._pixel_canvas.__setitem__(coordinates, new_pixel_value)
        except IndexError:
            pass


def _draw_on_frame(frame: _FrameCanvas, references_dict):
    try:
        highest_layer = max(references_dict) + 1
    except ValueError:
        return

    for index in range(highest_layer):
        if index not in references_dict:
            continue

        references = references_dict[index]
        for reference in references:
            if not reference.is_opened:
                reference.open()

            ref_x = reference.x
            ref_y = reference.y

            for x, y in itertools.product(
                    range(ref_x, ref_x + reference.get_image_width()),
                    range(ref_y, ref_y + reference.get_image_height())
            ):
                frame.update_pixel((x, y), reference.get_pixel_value((x - ref_x, y - ref_y)))


def _invoke_adjustment_duration(index: int, adj: Adjustment):
    # Assume that the `adj` has a 'duration' attribute.
    duration = index - adj.activation_time
    if duration > adj.duration:
        return adj.duration
    else:
        return duration


def create_frame(frame: _FrameCanvas, split_instructions: SeparatedInstructions):
    index = frame.index
    instructions = deepcopy(split_instructions)  # Avoid modifying the
    # original objects.
    layer_reference = {}
    merge_settings = {"mode": properties.MergeMode.REVERSE_APPEND}

    for ID, reference in instructions.references.items():
        try:
            relevant_adjustments = instructions.adjustments[ID]
        except KeyError:
            relevant_adjustments = None

        while relevant_adjustments:
            adj = relevant_adjustments.pop(0)

            if adj.activation_time > index:
                break

            args = ()
            if type(adj) is adjustments.core.MoveAdjustment:
                args = (_invoke_adjustment_duration(index, adj),)

            reference._properties = reference._properties.merge(adj._enact(*args), **merge_settings)

        if reference.visibility is properties.VisibilityStatus.HIDE:
            continue

        layer = reference.layer
        if layer not in layer_reference:
            layer_reference[layer] = set()

        layer_reference[layer].add(reference)

    _draw_on_frame(frame, layer_reference)
    frame.save()


def fill_undrawn_frames(temporary_directory: Path, video_length: int):
    with TemporaryAttribute(cleanup=_call_close) as frame_assignment:
        for index in range(video_length):
            try:
                frame_assignment.value = Image.open(
                    str(temporary_directory / f"{index:06d}.png")
                )
            except FileNotFoundError:
                frame_assignment.value.save(
                    temporary_directory / f"{index:06d}.png"
                )


def generate_frames(
        parsed_motion_tree: MotionTree,
        temporary_directory: Path,
        window_size: Tuple[int, int]
) -> Tuple[List[_FrameCanvas], int]:
    # ...
    frames = []
    index = 0

    for node in parsed_motion_tree.body:
        type_ = type(node)
        if type_ is motion_tree.Start:
            frames.append(_FrameCanvas(0, temporary_directory, window_size))
        elif type_ in (motion_tree.HideImage, motion_tree.MoveImage, motion_tree.ShowImage):
            if index == frames[-1].index:
                continue
            frames.append(_FrameCanvas(index, temporary_directory, window_size))
        elif type_ is motion_tree.InvokePrevious:
            start = 0
            if index == frames[-1].index:
                start = 1
                index += 1
            for _ in range(start, node.length):
                frames.append(_FrameCanvas(index, temporary_directory, window_size))
                index += 1
            del start
        elif type_ is motion_tree.Continue:
            index += node.length
        elif type_ is motion_tree.End:
            break

    return frames, index
