from __future__ import annotations

from .. import errors

from collections.abc import Hashable
import enum

from attrs import define, field


class Attribute(enum.Enum):
    BODY = enum.auto()
    ID = enum.auto()
    INDEX = enum.auto()
    LENGTH = enum.auto()
    TIME = enum.auto()


_attributes = {
    Attribute.BODY: ("body", list, field(factory=list, init=False)),
    Attribute.ID: ("id", Hashable, field()),
    Attribute.INDEX: ("index", int, field()),
    Attribute.LENGTH: ("length", int, field()),
    Attribute.TIME: ("time", int, field())
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
        raise errors.InternalError(f"Class \'{cls.__name__}\' does not define _attributes_.")

    for attr in cls._attributes_:
        try:
            _attributes[attr]
        except KeyError:
            raise errors.InternalError(f"Class \'{cls.__name__}\' has an undefined attribute: \'{attr}\'.")

    return wrapper()  # @dynamic_attributes
