from __future__ import annotations
import multiprocessing
import multiprocessing.pool
import inspect
import warnings
from typing import Any, Callable, Iterable, List


def parallelProcess(
    function: Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
    nJobs: int | None = None,
    chunkSize: int | None = None,
    overrideCPUCount: bool = False,
) -> List[Any]:
    """Creates a parallel pool with up to 'nJobs' processes to run a provided function on each element of an iterable.

    Parameters
    ----------
    function: Callable[[Any],Any]
        The function to run in parallel.
    args: Iterable[Any] | Iterable[Iterable[Any]]
        An iterable of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of an iterable of iterables.
    nJobs: int | None
        The number of processes to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        If unspecified, defaults to system logical CPU count.
    chunkSize: int | None
        The number of function executions on the iterable to pass to each process.
        If unspecified, defaults to heuristic calculation of divmod(len(args), nJobs * 4).
    overrideCPUCount: bool
        If set to True, the user provided nJobs is used as the number of processes to start simultaneously.
        This is done regardless of system resources available or possible Windows errors.
        Defaults to False.

    Returns
    -------
    List[Any]
        The outputs of the specified function across the iterable, in the provided order.
    """

    if nJobs is None and overrideCPUCount is True:
        warnings.warn(
            "nJobs is unset while overrideCPUCount is True, defaulting to system logical CPU Count.",
            RuntimeWarning,
        )

    if nJobs is None:
        nJobs: int = multiprocessing.cpu_count()

    if overrideCPUCount is True:
        nj: int = nJobs
    else:
        # The cap at 61 is due to possible windows errors.
        # See https://github.com/python/cpython/issues/71090
        nj: int = min(nJobs, multiprocessing.cpu_count(), 61)

    # Used as a default to reduce worker overhead.
    # Consider specifying smaller chunk sizes for small datasets.
    # See the below link for a discussion of the chosen default heuristic.
    # https://stackoverflow.com/questions/53751050/multiprocessing-understanding-logic-behind-chunksize
    if chunkSize is None:
        chunkSize, extra = divmod(len(args), nj * 4)
        if extra:
            chunkSize += 1

    with multiprocessing.Pool(processes=nj) as pool:
        print(f"Starting parallel pool with {nj} processes.".format(nj=nj))
        if len(inspect.signature(function).parameters) > 1:
            result: List[Any] = pool.starmap(
                func=function, iterable=args, chunksize=chunkSize
            )
        else:
            result: List[Any] = pool.map(
                func=function, iterable=args, chunksize=chunkSize
            )
    return result


def multiThread(
    function: Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
    nJobs: int | None = None,
    chunkSize: int | None = None,
    overrideCPUCount: bool = False,
) -> List[Any]:
    """Creates a parallel pool with up to 'nJobs' threads to run a provided function on each element of an iterable.

    Parameters
    ----------
    function: Callable[[Any],Any]
        The function to run in parallel.
    args: Iterable[Any] | Iterable[Iterable[Any]]
        An iterable of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of an iterable of iterables.
    nJobs: int | None
        The number of threads to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        If unspecified, defaults to system logical CPU count.
    chunkSize: int | None
        The number of function executions on the iterable to pass to each process.
        If unspecified, defaults to heuristic calculation of divmod(len(args), nJobs * 4).
    overrideCPUCount: bool
        If set to True, the user provided nJobs is used as the number of threads to start simultaneously.
        This is done regardless of system resources available or possible Windows errors.
        Defaults to False.

    Returns
    -------
    List[Any]
        The outputs of the specified function across the iterable, in the provided order.
    """

    if nJobs is None and overrideCPUCount is True:
        warnings.warn(
            "nJobs is unset while overrideCPUCount is True, defaulting to system logical CPU Count.",
            RuntimeWarning,
        )

    if nJobs is None:
        nJobs: int = multiprocessing.cpu_count()

    if overrideCPUCount is True:
        nj: int = nJobs
    else:
        # The cap at 61 is due to possible windows errors.
        # See https://github.com/python/cpython/issues/71090
        nj: int = min(nJobs, multiprocessing.cpu_count(), 61)

    # Used as a default to reduce worker overhead.
    # Consider specifying smaller chunk sizes for small datasets.
    # See the below link for a discussion of the chosen default heuristic.
    # https://stackoverflow.com/questions/53751050/multiprocessing-understanding-logic-behind-chunksize
    if chunkSize is None:
        chunkSize, extra = divmod(len(args), nj * 4)
        if extra:
            chunkSize += 1

    with multiprocessing.pool.ThreadPool(processes=nj) as pool:
        print(f"Starting parallel pool with {nj} threads.".format(nj=nj))
        if len(inspect.signature(function).parameters) > 1:
            result: List[Any] = pool.starmap(
                func=function, iterable=args, chunksize=chunkSize
            )
        else:
            result: List[Any] = pool.map(
                func=function, iterable=args, chunksize=chunkSize
            )
    return result
