"""Wrappers for multiprocessing.Pool and multiprocessing.pool.ThreadPool with TQDM progress bar integration."""

from __future__ import annotations
import multiprocessing
import multiprocessing.pool
import inspect
from typing import Any, Callable, Iterable, List

from ._helpers import _determineNJobs, _determineChunkSize


def parallelProcess(
    function: Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
    *,
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

    nJobs = _determineNJobs(nJobs=nJobs, overrideCPUCount=overrideCPUCount)

    chunkSize = _determineChunkSize(args=args, nJobs=nJobs, chunkSize=chunkSize)

    with multiprocessing.Pool(processes=nJobs) as pool:
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
    *,
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

    nJobs = _determineNJobs(nJobs=nJobs, overrideCPUCount=overrideCPUCount)

    chunkSize = _determineChunkSize(args=args, nJobs=nJobs, chunkSize=chunkSize)

    with multiprocessing.pool.ThreadPool(processes=nJobs) as pool:
        if len(inspect.signature(function).parameters) > 1:
            result: List[Any] = pool.starmap(
                func=function, iterable=args, chunksize=chunkSize
            )
        else:
            result: List[Any] = pool.map(
                func=function, iterable=args, chunksize=chunkSize
            )
    return result
