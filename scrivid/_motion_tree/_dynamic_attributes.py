from __future__ import annotations

from .. import errors

import enum

from attrs import define, field


class Attribute(enum.Enum):
    BODY = enum.auto()
    INDEX = enum.auto()
    LENGTH = enum.auto()


_attributes = {
    Attribute.BODY: ("body", list, field(factory=list, init=False)),
    Attribute.INDEX: ("index", int, field()),
    Attribute.LENGTH: ("length", int, field())
}


def _define_class(cls):
    if not hasattr(cls, "__annotations__"):
        cls.__annotations__ = {}

    name = 0
    annotation = 1
    value = 2

    for attr in cls._attributes_:
        attribute = _attributes[attr]
        cls.__annotations__[attribute[name]] = attribute[annotation]
        setattr(cls, attribute[name], attribute[value])

    cls = define(eq=False, frozen=True)(cls)
    return cls


def dynamic_attributes(cls=None, /):
    def wrapper():
        return _define_class(cls)

    if cls is None:  # @dynamic_attributes()
        return wrapper

    if not hasattr(cls, "_attributes_"):
        raise errors.UndefinedAttributesError(f"Class \'{cls.__name__}\' does not define _attributes_.")

    for attr in cls._attributes_:
        try:
            _attributes[attr]
        except KeyError:
            raise errors.InvalidAttributesError(f"Class \'{cls.__name__}\' has an undefined attribute: \'{attr}\'.")

    return wrapper()  # @dynamic_attributes
