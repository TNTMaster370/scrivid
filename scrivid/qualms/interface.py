from .. import errors

from abc import ABC, abstractmethod


class QualmInterface(ABC):
    __slots__ = ()

    code: str
    severity: int

    def __str__(self) -> str:
        message = self._message()
        return f":{self.code}:{self.severity}: {message}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, QualmInterface):
            raise errors.TypeError(f"Expected type QualmInterface, got type \'{other.__class__.__name__}\'")
        elif type(self) is not type(other):
            return False
        else:
            return self._comparison(other)

    @abstractmethod
    def _comparison(self, other) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _message(self) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def check(self):
        raise NotImplementedError
