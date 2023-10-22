from __future__ import annotations

from ._dynamic_attributes import Attribute, dynamic_attributes

import operator


def _compare_index(op: operator):
    def function(a, b):
        if not hasattr(b, "index"):
            return NotImplemented
        return op(a.index, b.index)

    return function


class RootMotionTree:
    __slots__ = ()


@dynamic_attributes
class Continue(RootMotionTree):
    _attributes_ = (Attribute.LENGTH,)


@dynamic_attributes
class End(RootMotionTree):
    _attributes_ = ()


@dynamic_attributes
class HideImage(RootMotionTree):
    _attributes_ = (Attribute.INDEX,)

    # For compatibility with sortedcontainers.SortedList.
    __eq__ = _compare_index(operator.eq)
    __ge__ = _compare_index(operator.ge)
    __gt__ = _compare_index(operator.gt)
    __le__ = _compare_index(operator.le)
    __lt__ = _compare_index(operator.lt)
    __ne__ = _compare_index(operator.ne)


@dynamic_attributes
class MotionTree(RootMotionTree):
    _attributes_ = (Attribute.BODY,)

    def convert_to_string(self, *, indent: int = 0, _previous_indent: int = 0):
        if len(self.body) == 0:
            return repr(self)

        indent_sequence = ""
        if indent > 0:
            indent_sequence = f"\n{' ' * _previous_indent}"

        return (
            f"{indent_sequence}{self.__class__.__name__}("
            + f"{indent_sequence}{' ' * indent}body=["
            + ', '.join(
                node.convert_to_string(indent=indent, _previous_indent=(2*indent)+_previous_indent)
                if getattr(node, "convert_to_string", False)
                else f"{indent_sequence}{' ' * (2 * indent)}{node!r}"
                for node in self.body)
            + "])"
        )


@dynamic_attributes
class ShowImage(RootMotionTree):
    _attributes_ = (Attribute.INDEX,)

    # For compatibility with sortedcontainers.SortedList.
    __eq__ = _compare_index(operator.eq)
    __ge__ = _compare_index(operator.ge)
    __gt__ = _compare_index(operator.gt)
    __le__ = _compare_index(operator.le)
    __lt__ = _compare_index(operator.lt)
    __ne__ = _compare_index(operator.ne)


@dynamic_attributes
class Start(RootMotionTree):
    _attributes_ = ()
