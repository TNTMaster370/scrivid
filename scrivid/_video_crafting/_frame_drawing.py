from __future__ import annotations

from ._frame_info import FrameInfo

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


def _draw_on_frame(frame: FrameInfo, references_dict):
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
                frame.canvas.set_pixel((x, y), reference.get_pixel_value((x - ref_x, y - ref_y)))


def _invoke_adjustment_duration(index: int, adj: Adjustment):
    # Assume that the `adj` has a 'duration' attribute.
    duration = index - adj.activation_time
    if duration > adj.duration:
        return adj.duration
    else:
        return duration


def create_frame(frame: FrameInfo, split_instructions: SeparatedInstructions):
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
    frame.canvas.save(frame.save_file)


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
) -> Tuple[List[FrameInfo], int]:
    # ...
    frames = []
    index = 0

    for node in parsed_motion_tree.body:
        type_ = type(node)
        if type_ is motion_tree.Start:
            frames.append(FrameInfo(0, temporary_directory, window_size))
        elif type_ in (motion_tree.HideImage, motion_tree.MoveImage, motion_tree.ShowImage):
            if index == frames[-1].index:
                continue
            frames.append(FrameInfo(index, temporary_directory, window_size))
        elif type_ is motion_tree.InvokePrevious:
            start = 0
            if index == frames[-1].index:
                start = 1
                index += 1
            for _ in range(start, node.length):
                frames.append(FrameInfo(index, temporary_directory, window_size))
                index += 1
            del start
        elif type_ is motion_tree.Continue:
            index += node.length
        elif type_ is motion_tree.End:
            break

    return frames, index
