from typing import Callable, Any


def _fStar(function: Callable[[Any],Any], args) -> Callable[[Any],Any]:
    """Starmap a function with provided arguments.
    Used with TQDM variants of multiThreading and parallelProcess

    Parameters
    ----------
    function : Callable
        The function to pass arguments to.
    args : Iterable
        The arguments to unpack.

    Returns
    -------
    function(*args) : Callable[[Any],Any]
        The specified function with arguments unpacked and passed to it.
    """
    return function(*args)
