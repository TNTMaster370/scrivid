class SentinelBase(type):
    def __new__(mcs, *_, **__):
        raise TypeError(f"{mcs!r} is not callable")

    def __repr__(self):
        return self.__name__


def sentinel(name):
    cls = type.__new__(SentinelBase, name, (SentinelBase,), {})
    cls.__class__ = cls
    return cls
