def get_args(tp):
    """Backport of typing.get_args for Python 3.6"""
    return getattr(tp, "__args__", ())


def get_origin(tp):
    """Backport of typing.get_origin for Python 3.6"""
    return getattr(tp, "__origin__", None)
