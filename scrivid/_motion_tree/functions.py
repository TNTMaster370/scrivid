from __future__ import annotations

from .nodes import Continue, End, HideImage, InvokePrevious, MotionTree, MoveImage, ShowImage, Start
from .._file_objects.adjustments import HideAdjustment, MoveAdjustment, ShowAdjustment
from .._separating_instructions import separate_instructions, SeparatedInstructions

from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from .._file_objects.adjustments import RootAdjustment
    from .._file_objects.images import ImageReference

    from collections.abc import Sequence
    from typing import Dict, Iterator, Optional, Union

    MOTION_NODES = Union[Continue, End, HideImage, MotionTree, ShowImage, Start]
    REFERENCES = ImageReference


def dump(motion_tree: MotionTree, *, indent: int = 0) -> str:
    if hasattr(motion_tree, "convert_to_string"):
        return motion_tree.convert_to_string(indent=indent).strip()
    else:
        return repr(motion_tree)


def _create_command_node(adjustment: RootAdjustment) -> Optional[Union[HideImage, MoveImage, ShowImage]]:
    adjustment_type = type(adjustment)
    adjustment_time = adjustment.activation_time
    relevant_id = adjustment.ID

    if adjustment_type == HideAdjustment:
        return HideImage(relevant_id, adjustment_time)
    elif adjustment_type == MoveAdjustment:
        return MoveImage(relevant_id, adjustment_time, adjustment.duration)
    elif adjustment_type == ShowAdjustment:
        return ShowImage(relevant_id, adjustment_time)
    else:
        return None


def _create_motion_tree(separated_instructions: SeparatedInstructions) -> MotionTree:
    motion_tree = MotionTree()

    motion_tree.body.append(Start())

    for node in _loop_over_adjustments(separated_instructions.adjustments):
        motion_tree.body.append(node)

    motion_tree.body.append(End())

    return motion_tree


def _invoke_duration_value(duration_value: int, current_node: Union[HideImage, MoveImage, ShowImage]) -> int:
    if not hasattr(current_node, "duration"):
        return duration_value

    if duration_value == 0 or duration_value <= current_node.duration:
        return current_node.duration
    else:
        return duration_value


def _loop_over_adjustments(adjustments: Dict[RootAdjustment]) -> Iterator[MOTION_NODES]:
    current_node = None
    duration_value = 0
    sorted_adjustments = SortedList(
        id_of_adj_value 
        for adj_value in adjustments.values() 
        for id_of_adj_value in adj_value
    )
    time_index = 0

    while sorted_adjustments or current_node:
        if current_node is None:
            adjustment = sorted_adjustments.pop(0)
            current_node = _create_command_node(adjustment)

        if current_node.time <= time_index:
            yield current_node
            duration_value = _invoke_duration_value(
                duration_value, current_node
            )
            current_node = None
            continue

        time_difference = current_node.time - time_index

        if duration_value != 0 and duration_value <= time_difference:
            duration_value = _invoke_duration_value(duration_value, current_node)
            yield InvokePrevious(duration_value)
            time_index += duration_value
            duration_value = 0
            continue

        elif duration_value != 0 and duration_value > time_difference:
            yield InvokePrevious(time_difference)
            time_index += time_difference
            duration_value = _invoke_duration_value((duration_value - time_difference), current_node)
            continue

        else:
            yield Continue(time_difference)
            time_index += time_difference

        yield current_node

        duration_value = _invoke_duration_value(duration_value, current_node)
        current_node = None

    if current_node is not None:
        duration_value = _invoke_duration_value(duration_value, current_node)
    if duration_value != 0:
        yield InvokePrevious(duration_value)


def parse(instructions: Union[Sequence[REFERENCES], SeparatedInstructions]) -> MotionTree:
    if not isinstance(instructions, SeparatedInstructions):
        instructions = separate_instructions(instructions)

    return _create_motion_tree(instructions)


def walk(motion_tree: MotionTree) -> Iterator[MOTION_NODES]:
    yield motion_tree

    if not hasattr(motion_tree, "body"):
        return

    for node in motion_tree.body:
        if hasattr(node, "body"):
            for additional_node in walk(node):
                yield additional_node
            continue

        yield node
