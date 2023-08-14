class _SentinelBase(type):
    def __new__(mcs, *args, **kwargs):
        raise TypeError(f"{mcs!r} is not callable")

    def __repr__(self):
        return self.__name__


def sentinel(name):
    cls = type.__new__(_SentinelBase, name, (_SentinelBase,), {})
    cls.__class__ = cls
    return cls
