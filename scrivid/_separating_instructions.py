from __future__ import annotations

from . import errors
from ._file_objects.images import ImageReference

from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from ._file_objects.adjustments import RootAdjustment

    from collections.abc import Sequence
    from typing import Dict, Hashable

    REFERENCES = ImageReference


class SeparatedInstructions:
    __slots__ = ("adjustments", "references")

    adjustments: Dict[Hashable, SortedList[RootAdjustment]]
    references: Dict[Hashable, ImageReference]

    def __init__(self):
        self.adjustments = {}
        self.references = {}


def separate_instructions(references: Sequence[REFERENCES]) -> SeparatedInstructions:
    separated_instructions = SeparatedInstructions()

    for reference in references:
        if reference.ID in separated_instructions.references:
            raise errors.DuplicateIDError(duplicate_id=reference.ID)
        separated_instructions.references[reference.ID] = reference
        for adjustment in reference.adjustments:
            if reference.ID not in separated_instructions.adjustments:
                separated_instructions.adjustments[reference.ID] = SortedList()
            separated_instructions.adjustments[reference.ID].add(adjustment)

    return separated_instructions
