from .. import errors


def check_hashable(name, value):
    try:
        hash(value)
    except TypeError:
        raise errors.TypeError(f"`{name}` must be hashable.")


def check_inheritance(name, value, root):
    if not isinstance(value, root):
        raise errors.TypeError(f"`{name}` must be an instance of `{root}` or a subclass of it.")


def check_int(name, value):
    if not isinstance(value, int) or isinstance(value, bool):
        raise errors.TypeError(f"`{name}` must be an integer.")
