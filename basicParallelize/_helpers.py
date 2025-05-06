from typing import Any, Callable, Iterable


def _fStar(function: Callable[[Any],Any], args: Iterable[Any] | Iterable[Iterable[Any]]) -> Callable[[Any],Any]:
    """Starmap a function with provided arguments.
    Used with TQDM variants of multiThreading and parallelProcess

    Parameters
    ----------
    function : Callable[[Any],Any]
        The function to pass arguments to.
    args : Iterable[Any] | Iterable[Iterable[Any]]
        The arguments to unpack.

    Returns
    -------
    function(*args) : Callable[[Any],Any]
        The specified function with arguments unpacked and passed to it.
    """
    return function(*args)
