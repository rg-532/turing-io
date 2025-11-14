
class ClassNotFoundError(ValueError):
    """Raised when attempting to decode with ``jsonpickle``, and it encounters a :class:`ClassNotFoundError`.

    The reasoning for this is to override the author's decision to define :class:`ClassNotFoundError` to inherit
    from ``BaseException`` instead of ``Exception`` as expected, meaning it cannot be caught with a global ``except``
    ``Exception`` ``...`` clause (Needed for implementations which parse the error before handling it).
    """
    pass
