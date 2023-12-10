from abc import ABC, abstractmethod


class QualmInterface(ABC):
    __slots__ = ()

    code: str
    severity: int

    def __str__(self) -> str:
        message = self._message()
        return f":{self.code}:{self.severity}: {message}"

    @abstractmethod
    def _message(self) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def check(self):
        raise NotImplementedError
