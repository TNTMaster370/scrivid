from __future__ import annotations

from .nodes import Continue, End, HideImage, MotionTree, ShowImage, Start
from .._file_objects.adjustments import HideAdjustment, ShowAdjustment
from .._id_check import check_reference_id
from .._utils import sentinel

from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from .._file_objects.adjustments import RootAdjustment
    from .._file_objects.images import ImageReference

    from collections.abc import Sequence
    from typing import Iterator, Union

    MOTION_NODES = Union[Continue, End, HideImage, MotionTree, ShowImage, Start]
    REFERENCES = ImageReference


def dump(motion_tree: MotionTree, *, indent: int = 0) -> str:
    if hasattr(motion_tree, "convert_to_string"):
        return motion_tree.convert_to_string(indent=indent).strip()
    else:
        return repr(motion_tree)


def _create_command_node(reference_id, adjustment: RootAdjustment) -> Union[HideImage, ShowImage, None]:
    # INITIALIZE
    adjustment_type = type(adjustment)
    adjustment_time = adjustment.activation_time

    # OPERATION/TEARDOWN
    if adjustment_type == HideAdjustment:
        return HideImage(reference_id, adjustment_time)
    elif adjustment_type == ShowAdjustment:
        return ShowImage(reference_id, adjustment_time)
    else:
        return None


def _create_command_node_list(references: Sequence[REFERENCES]) -> SortedList[HideImage, ShowImage]:
    # INITIALIZE
    command_node_list = SortedList()

    # OPERATION
    for reference in references:
        adjustments = reference.adjustments
        for adjustment in adjustments:
            command_node = _create_command_node(reference.id, adjustment)
            if command_node is None:
                raise TypeError
            command_node_list.add(command_node)

    # TEARDOWN
    return command_node_list


def _fill_motion_tree(motion_tree: MotionTree, command_node_list: SortedList[HideImage, ShowImage]):
    # INITIALIZE
    index = 0
    UNFILLED = sentinel("UNFILLED")
    current_node = UNFILLED

    # OPERATION
    while command_node_list:
        if current_node is UNFILLED:
            current_node = command_node_list.pop(0)

        if current_node.time > index:
            difference = current_node.time - index
            motion_tree.body.append(Continue(difference))
            index += difference
            continue

        motion_tree.body.append(current_node)
        current_node = UNFILLED

    if current_node is not UNFILLED:
        motion_tree.body.append(current_node)


def parse(references: Sequence[REFERENCES]) -> MotionTree:
    # GATEKEEP
    check_reference_id(references)

    # INITIALIZE
    motion_tree = MotionTree()
    motion_tree.body.append(Start())

    command_node_list = _create_command_node_list(references)

    # OPERATION
    _fill_motion_tree(motion_tree, command_node_list)

    # TEARDOWN
    motion_tree.body.append(End())
    return motion_tree


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
