"""Wrappers for multiprocessing.Pool and multiprocessing.pool.ThreadPool with TQDM progress bar integration."""

from __future__ import annotations
import multiprocessing
import multiprocessing.pool
import functools
import inspect
from typing import Any, Callable, Iterable, List

import tqdm

from ._helpers import _determineNJobs, _determineChunkSize


def _fStar(
    function: Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
) -> Callable[[Any], Any]:
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


# R0913 Too-Many-Arguments warning is disabled as providing a single contact point for end users is the goal.
# Sensible defaults are provided to reduce mental burden while still allowing customization for advanced use.
def parallelProcessTQDM(  # pylint: disable=too-many-arguments
    function: Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
    *,
    nJobs: int | None = None,
    chunkSize: int | None = None,
    overrideCPUCount: bool = False,
    description: str | None = None,
) -> List[Any]:
    """Creates a parallel pool with up to 'nJobs' processes to run a provided function on each element of an iterable.
    Displays a TQDM progress bar.

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
    description: str | None
        If present, sets the string to display on the TQDM progress bar.

    Returns
    -------
    List[Any]
        The outputs of the specified function across the iterable, in the provided order.
    """

    nJobs = _determineNJobs(nJobs=nJobs, overrideCPUCount=overrideCPUCount)

    chunkSize = _determineChunkSize(args=args, nJobs=nJobs, chunkSize=chunkSize)

    with multiprocessing.Pool(processes=nJobs) as pool:
        print(f"Starting parallel pool with {nJobs} processes.".format(nJobs=nJobs))
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
        else:
            result: List[Any] = list(
                tqdm.tqdm(
                    pool.imap(func=function, iterable=args, chunksize=chunkSize),
                    total=len(args),
                    desc=description,
                )
            )
    return result


# R0913 Too-Many-Arguments warning is disabled as providing a single contact point for end users is the goal.
# Sensible defaults are provided to reduce mental burden while still allowing customization for advanced use.
def multiThreadTQDM(  # pylint: disable=too-many-arguments
    function: Callable[[Any], Any],
    args: Iterable[Any] | Iterable[Iterable[Any]],
    *,
    nJobs: int | None = None,
    chunkSize: int | None = None,
    overrideCPUCount: bool = False,
    description: str | None = None,
) -> List[Any]:
    """Creates a parallel pool with up to 'nJobs' threads to run a provided function on each element of an iterable.
    Displays a TQDM progress bar.

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
    description: str | None
        If present, sets the string to display on the TQDM progress bar.

    Returns
    -------
    List[Any]
        The outputs of the specified function across the iterable, in the provided order.
    """

    nJobs = _determineNJobs(nJobs=nJobs, overrideCPUCount=overrideCPUCount)

    chunkSize = _determineChunkSize(args=args, nJobs=nJobs, chunkSize=chunkSize)

    with multiprocessing.pool.ThreadPool(processes=nJobs) as pool:
        print(f"Starting parallel pool with {nJobs} threads.".format(nJobs=nJobs))
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
        else:
            result: List[Any] = list(
                tqdm.tqdm(
                    pool.imap(func=function, iterable=args, chunksize=chunkSize),
                    total=len(args),
                    desc=description,
                )
            )
    return result
