from __future__ import annotations

import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterator, Optional


def _copy_iterator(iterator) -> Iterator:
    return copy.deepcopy(iterator)


def _recursively_loop_over_additional_iter(iter_):
    if len(iter_) == 1:
        for item in iter_[0]:
            yield item

        return

    for item in iter_[0]:
        copy_of_iters = tuple(_copy_iterator(i) for i in iter_[1:])

        for additional_items in _recursively_loop_over_additional_iter(copy_of_iters):
            if isinstance(additional_items, (list, tuple)):
                complete_items = (item, *additional_items)
            else:
                complete_items = (item, additional_items)

            yield complete_items


def ticking(*iter_) -> Optional[Iterator]:
    if not iter_:
        return

    for items in _recursively_loop_over_additional_iter(iter_):
        yield items
