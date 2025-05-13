"""Helper functions for shared logic between _parallelize.py and _parallelizeTQDM.py."""

from __future__ import annotations
import functools
import inspect
import multiprocessing
import multiprocessing.pool
import warnings
from typing import Any, Callable, Iterable, List

import tqdm


def _determineChunkSize(
    function: Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
    nJobs: int | None = None,
    chunkSize: int | None = None,
) -> int:
    """Determines appropriate chunk size for distributing the total work across the parallel pool.

    Parameters
    ----------
    args: Iterable[Any] | Iterable[Iterable[Any]]
        An iterable of parameters to pass to the target function.
    nJobs: int | None
        The number of processes or threads to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        If unspecified, defaults to system logical CPU count.
    chunkSize: int | None
        The number of function executions on the iterable to pass to each process or thread.
        If unspecified, defaults to heuristic calculation of divmod(len(args), nJobs * 4).

    Returns
    -------
    int
        The number of function executions on the iterable to send to each process or thread.
    """

    if len(inspect.signature(function).parameters) != 0:
        # Used as a default to reduce worker overhead.
        # Consider specifying smaller chunk sizes for small datasets.
        # Alternatively, consider the heuristic calculation of math.ceil(len(args) / nJobs)) for large datasets.
        # See the below link for a discussion of the chosen default heuristic.
        # https://stackoverflow.com/questions/53751050/multiprocessing-understanding-logic-behind-chunksize
        if chunkSize is None:
            chunkSize, extra = divmod(len(args), nJobs * 4)
            if extra:
                chunkSize += 1
    else:
        if chunkSize is not None:
            warnings.warn(
                "chunkSize is set while the function requires no parameters. Ignoring chunkSize.",
                UserWarning,
            )

    return chunkSize


def _determineNJobs(
    nJobs: int | None = None,
    overrideCPUCount: bool = False,
) -> int:
    """Determines the number of processes or threads to start in a parallel pool.

    Parameters
    ----------
    nJobs: int | None
        The number of processes or threads to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        If unspecified, defaults to system logical CPU count.
    overrideCPUCount: bool
        If set to True, the user provided nJobs is used as the number of processes to start simultaneously.
        This is done regardless of system resources available or possible Windows errors.
        Defaults to False.

    Returns
    -------
    int
        The number of processes or threads to start simultaneously.
    """
    if nJobs is None and overrideCPUCount is True:
        warnings.warn(
            "nJobs is unset while overrideCPUCount is True, defaulting to system logical CPU Count.",
            UserWarning,
        )
    if nJobs is None:
        nJobs: int = multiprocessing.cpu_count()
    if overrideCPUCount is True:
        nJobs: int = nJobs
    else:
        # The cap at 61 is due to possible windows errors.
        # See https://github.com/python/cpython/issues/71090
        nJobs: int = min(nJobs, multiprocessing.cpu_count(), 61)
    return nJobs


def _fStar(
    function: Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
) -> Callable[[Any], Any]:
    """Starmap a function with provided arguments.

    Parameters
    ----------
    function : Callable[[Any], Any]
        The function to pass arguments to.
    args : Iterable[Any] | Iterable[Iterable[Any]]
        The arguments to unpack.

    Returns
    -------
    function(*args) : Callable[[Any],Any]
        The specified function with arguments unpacked and passed to it.
    """
    return function(*args)


def _flexibleMap(
    pool: multiprocessing.pool.Pool | multiprocessing.pool.ThreadPool,
    function: Callable[[], Any] | Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
    chunkSize: int,
) -> List[Any]:
    """Automatically determine the appropriate map type for a function and process arguments in parallel.

    Parameters
    ----------
    pool: multiprocessing.pool.Pool | multiprocessing.pool.ThreadPool
        The pool or threadpool whose workers are used for parallel processing.
    function: Callable[[], Any] | Callable[[Any], Any]
        The function to run in parallel.
    args: Iterable[Any] | Iterable[Iterable[Any]]
        An iterable of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of an iterable of iterables.
        If the function requires no parameters, the length of the iterable determines the number of function executions.
    chunkSize: int
        The number of function executions on the iterable to pass to each process.

    Returns
    -------
    List[Any]
        The outputs of the specified function across the iterable, in the provided order.
    """
    if len(inspect.signature(function).parameters) > 1:
        result: List[Any] = pool.starmap(
            func=function, iterable=args, chunksize=chunkSize
        )
    elif len(inspect.signature(function).parameters) == 1:
        result: List[Any] = pool.map(func=function, iterable=args, chunksize=chunkSize)
    else:
        result: List[multiprocessing.pool.ApplyResult] = list(
            pool.apply_async(func=function) for __ in range(len(args))
        )
        result: List[Any] = [item.get() for item in result]
    return result


def _flexibleMapTQDM(
    pool: multiprocessing.pool.Pool | multiprocessing.pool.ThreadPool,
    function: Callable[[], Any] | Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
    chunkSize: int,
    description: str | None = None,
) -> List[Any]:
    """Automatically determine the appropriate map type for a function and process arguments in parallel.
    Used with TQDM variants of multiThreading and parallelProcess

    Parameters
    ----------
    pool: multiprocessing.pool.Pool | multiprocessing.pool.ThreadPool
        The pool or threadpool whose workers are used for parallel processing.
    function: Callable[[], Any] | Callable[[Any], Any]
        The function to run in parallel.
    args: Iterable[Any] | Iterable[Iterable[Any]]
        An iterable of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of an iterable of iterables.
        If the function requires no parameters, the length of the iterable determines the number of function executions.
    chunkSize: int
        The number of function executions on the iterable to pass to each process.
    description: str | None
        If present, sets the string to display on the TQDM progress bar.

    Returns
    -------
    List[Any]
        The outputs of the specified function across the iterable, in the provided order.
    """
    if len(inspect.signature(function).parameters) > 1:
        result: List[Any] = list(
            tqdm.tqdm(
                pool.imap(
                    func=functools.partial(_fStar, function),
                    iterable=args,
                    chunksize=chunkSize,
                ),
                total=len(args),
                desc=description,
            )
        )
    elif len(inspect.signature(function).parameters) == 1:
        result: List[Any] = list(
            tqdm.tqdm(
                pool.imap(func=function, iterable=args, chunksize=chunkSize),
                total=len(args),
                desc=description,
            )
        )
    else:
        result: List[multiprocessing.pool.ApplyResult] = list(
            tqdm.tqdm(
                (pool.apply_async(func=function) for __ in range(len(args))),
                total=len(args),
                desc=description,
            )
        )
        result: List[Any] = [item.get() for item in result]
    return result
