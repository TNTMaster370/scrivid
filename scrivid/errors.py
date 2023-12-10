from __future__ import annotations

import re
import textwrap
from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from typing import Any, Hashable


# Normally I'd write classes myself, without using dataclasses or attrs. This
# is because I like to see *exactly* what code is being run. That said, I don't
# *really* care about the implementation details for these Exception objects,
# since these classes need simple value initializing (except for the message
# attribute), and frozen attribute access. I import attrs since it has slots
# access, and I need something like it regarding the motion_tree nodes, but I
# think it's safe to use here as well, since I only care about the attributes
# and not anything like __repr__ or hidden variables.


def _replace_in_string(
        string: str,
        new_section: str,
        start: int,
        end: int
) -> str:
    # ...
    return string[:start] + new_section + string[end:]


def _use_default_message_name(err: ScrividException) -> str:
    message = err.default_message
    while (match := re.search(r"[\{]{2}([\w_]+)[\}]{2}", message)) is not None:
        r = match.span()
        n = str(getattr(err, message[r[0]:r[1]].strip("{}")))
        message = _replace_in_string(message, n, *r)
    return message


class ScrividException(Exception):
    """ Base class for all Exceptions that are propagated from Scrivid. """


class AttributeError(ScrividException):
    ...


@define(frozen=True)
class ConflictingAttributesError(AttributeError):
    """
    An exception that is propagated when two attribute values conflict with 
    each other.
    """

    default_message = textwrap.dedent("""
        Conflicting attributes: \'{{first_name}}\' (set to {{first_value}}) and
         \'{{second_name}}\' (set to {{second_value}})."
    """).replace("\n", "")

    first_name: Any = field(kw_only=True)
    first_value: Any = field(kw_only=True)
    second_name: Any = field(kw_only=True)
    second_value: Any = field(kw_only=True)
    message: str = field(kw_only=True)

    @message.default
    def _default_message(self):
        return _use_default_message_name(self)


@define(frozen=True)
class DuplicateIDError(ScrividException):
    """ An exception that is propagated when there is a duplicate ID field. """

    default_message = textwrap.dedent("""
        Duplicate ID field found between multiple identical objects: \'{{duplic
        ate_id}}\'
    """).replace("\n", "")

    duplicate_id: Hashable = field(kw_only=True)
    message: str = field(kw_only=True)

    @message.default
    def _default_message(self):
        return _use_default_message_name(self)


@define(frozen=True)
class InternalError(ScrividException):
    """
    An exception that should only be propagated when something in the internals
    of Scrivid functionality goes wrong. This should not be externally accessed
    except for debugging functionality.
    """
    exc: Exception = field(repr=False)

    @property
    def message(self):
        return f"There was an internal error that occured: {self.exc}"


@define(frozen=True)
class InternalErrorFromFFMPEG(InternalError):
    stdout: Any = field(repr=False)
    stderr: Any = field(repr=False)


class OperatorError(ScrividException):
    ...


class TypeError(ScrividException):
    ...
