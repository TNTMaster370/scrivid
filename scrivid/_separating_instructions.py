from __future__ import annotations

from . import errors
from ._file_objects.adjustments import RootAdjustment
from ._file_objects.images import ImageReference

from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Dict, Hashable, Union

    INSTRUCTIONS = Union[ImageReference, RootAdjustment]
    REFERENCES = ImageReference


class SeparatedInstructions:
    __slots__ = ("adjustments", "references")

    adjustments: Dict[Hashable, SortedList[RootAdjustment]]
    references: Dict[Hashable, ImageReference]

    def __init__(self):
        self.adjustments = {}
        self.references = {}


def _handle_adjustment(
        separated_instructions: SeparatedInstructions,
        adjustment: RootAdjustment
):
    if adjustment.ID not in separated_instructions.adjustments:
        separated_instructions.adjustments[adjustment.ID] = SortedList()

    if adjustment in separated_instructions.adjustments[adjustment.ID]:  
        # Safety against multiple declaration of Adjustment via also being
        # inside of the relevant ImageReference's .adjustment attribute.
        return

    separated_instructions.adjustments[adjustment.ID].add(adjustment)


def _handle_reference(
        separated_instructions: SeparatedInstructions,
        reference: REFERENCES
):
    if reference.ID in separated_instructions.references:
        raise errors.DuplicateIDError(duplicate_id=reference.ID)

    separated_instructions.references[reference.ID] = reference


def separate_instructions(
        instructions: Sequence[INSTRUCTIONS]
) -> SeparatedInstructions:
    # ...
    separated_instructions = SeparatedInstructions()

    for instruction in instructions:
        if isinstance(instruction, ImageReference):
            _handle_reference(separated_instructions, instruction)
        elif isinstance(instruction, RootAdjustment):
            _handle_adjustment(separated_instructions, instruction)

    return separated_instructions
