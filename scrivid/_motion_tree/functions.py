from __future__ import annotations

from .nodes import Continue, End, HideImage, MotionTree, ShowImage, Start
from .._file_objects.adjustments import HideAdjustment, ShowAdjustment
from .._separating_instructions import check_reference_id, separate_instructions, SeparatedInstructions

from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from .._file_objects.adjustments import RootAdjustment
    from .._file_objects.images import ImageReference

    from collections.abc import Sequence
    from typing import Dict, Iterator, Union

    MOTION_NODES = Union[Continue, End, HideImage, MotionTree, ShowImage, Start]
    REFERENCES = ImageReference


def dump(motion_tree: MotionTree, *, indent: int = 0) -> str:
    if hasattr(motion_tree, "convert_to_string"):
        return motion_tree.convert_to_string(indent=indent).strip()
    else:
        return repr(motion_tree)


def _create_command_node(adjustment: RootAdjustment) -> Union[HideImage, ShowImage, None]:
    # INITIALIZE
    adjustment_type = type(adjustment)
    adjustment_time = adjustment.activation_time
    relevant_id = adjustment.ID

    # OPERATION/TEARDOWN
    if adjustment_type == HideAdjustment:
        return HideImage(relevant_id, adjustment_time)
    elif adjustment_type == ShowAdjustment:
        return ShowImage(relevant_id, adjustment_time)
    else:
        return None


def _create_motion_tree(separated_instructions: SeparatedInstructions) -> MotionTree:
    # INITIALIZE
    motion_tree = MotionTree()

    # OPERATION
    motion_tree.body.append(Start())

    for node in _loop_over_adjustments(separated_instructions.adjustments):
        motion_tree.body.append(node)

    motion_tree.body.append(End())

    # TEARDOWN
    return motion_tree


def _loop_over_adjustments(adjustments: Dict[RootAdjustment]) -> Iterator[MOTION_NODES]:
    sorted_adjustments = SortedList(
        id_of_adj_value 
        for adj_value in adjustments.values() 
        for id_of_adj_value in adj_value
    )
    time_index = 0

    for adjustment in sorted_adjustments:
        current_node = _create_command_node(adjustment)

        if current_node.time > time_index:
            difference = current_node.time - time_index
            yield Continue(difference)
            time_index += difference

        if current_node is None:
            raise TypeError

        yield current_node


def parse(instructions: Union[Sequence[REFERENCES], SeparatedInstructions]) -> MotionTree:
    if not isinstance(instructions, SeparatedInstructions):
        instructions = separate_instructions(instructions)

    check_reference_id(instructions.references)

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
