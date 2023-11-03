from __future__ import annotations

from . import errors

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._file_objects.images import ImageReference

    from collections.abc import Sequence

    REFERENCES = ImageReference


def check_reference_id(references: Sequence[REFERENCES]):
    seen = set()
    for reference in references:
        if reference.id in seen:
            raise errors.DuplicateIDError(duplicate_id=reference.id)
        seen.add(reference.id)
