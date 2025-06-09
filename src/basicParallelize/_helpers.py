"""Helper functions for shared logic between _parallelize.py and _parallelizeTQDM.py."""

from __future__ import annotations

import functools
import inspect
import multiprocessing
import multiprocessing.pool
import warnings
from typing import Any, Callable, Sequence

import tqdm


def _determineChunkSize(
    *,
    function: Callable[..., Any],
    args: Sequence[Any] | Sequence[Sequence[Any]],
    nJobs: int,
    chunkSize: int | None = None,
) -> int | None:
    """Determines appropriate chunk size for distributing the total work across the parallel pool.

    Parameters
    ----------
    function: Callable[..., Any]
        The function being run in parallel.
    args: Sequence[Any] | Sequence[Sequence[Any]]
        A sequence of parameters to pass to the target function.
    nJobs: int | None
        The number of processes or threads to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        If unspecified, defaults to system logical CPU count.
    chunkSize: int | None
        The number of function executions on the sequence to pass to each process or thread.
        If unspecified, defaults to heuristic calculation of divmod(len(args), nJobs * 4).

    Returns:
    -------
    int
        The number of function executions on the sequence to send to each process or thread.

    Warnings:
    --------
    UserWarning
        If `chunkSize` is specified while `function` requires no parameters, a warning is issued to notify users that
        the specified `chunkSize` has no effect.
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
    elif chunkSize is not None:
        warnings.warn(
            "chunkSize is set while the function requires no parameters. Ignoring chunkSize.",
            UserWarning,
            stacklevel=2,
        )

    return chunkSize


def _determineNJobs(
    *,
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
        If set to True, the user provided `nJobs` is used as the number of processes to start simultaneously.
        This is done regardless of system resources available or possible Windows errors.
        Defaults to False.

    Returns:
    -------
    int
        The number of processes or threads to start simultaneously.

    Warnings:
    --------
    UserWarning
        If `nJobs` is None while `overrideCPUCount` is True, a warning is issued to notify users that they
        may have forgotten to specify `nJobs` or unintentinally specified `overrideCPUCount`.
    """
    if nJobs is None:
        if overrideCPUCount is True:
            warnings.warn(
                "nJobs is unset while overrideCPUCount is True, defaulting to system logical CPU Count.",
                UserWarning,
                stacklevel=2,
            )
        nJobs = multiprocessing.cpu_count()
    if overrideCPUCount is False:
        # The cap at 61 is due to possible windows errors.
        # See https://github.com/python/cpython/issues/71090
        nJobs = min(nJobs, multiprocessing.cpu_count(), 61)
    return nJobs


def _fStar(
    function: Callable[..., Any],
    args: Sequence[Any] | Sequence[Sequence[Any]],
) -> Callable[..., Any]:
    """Starmap a function with provided arguments.

    Parameters
    ----------
    function : Callable[..., Any]
        The function to pass arguments to.
    args : Sequence[Any] | Sequence[Sequence[Any]]
        The arguments to unpack.

    Returns:
    -------
    function(*args) : Callable[..., Any]
        The specified function with arguments unpacked and passed to it.
    """
    return function(*args)


def _flexibleMap(
    *,
    pool: multiprocessing.pool.Pool | multiprocessing.pool.ThreadPool,
    function: Callable[..., Any],
    args: Sequence[Any] | Sequence[Sequence[Any]],
    chunkSize: int | None,
) -> list[Any]:
    """Automatically determine the appropriate map type for a function and process arguments in parallel.

    Parameters
    ----------
    pool: multiprocessing.pool.Pool | multiprocessing.pool.ThreadPool
        The pool or threadpool whose workers are used for parallel processing.
    function: Callable[..., Any]
        The function to run in parallel.
    args: Sequence[Any] | Sequence[Sequence[Any]]
        A sequence of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of a sequence of sequences.
        If the function requires no parameters, the length of the sequence determines the number of function executions.
    chunkSize: int
        The number of function executions on the sequence to pass to each process.

    Returns:
    -------
    list[Any]
        The outputs of the specified function across the sequence, in the provided order.

    Raises:
    ------
    TypeError
        If a generator function is provided as 'function' a TypeError is raised.
        They are intentionally unsupported as parallelization of calls to non trivial generators
        requires knowledge of the generator's internal state.
    """
    # Generators are unsupported as their internal state must be known to parallelize calls to them
    # which would negate the purpose of calling the generator in the first place.
    # See https://stackoverflow.com/questions/7972295/python-generator-unpack-entire-generator-in-parallel
    if inspect.isgeneratorfunction(function):
        msg: str = "Generator functions are intentionally unsupported."
        raise TypeError(msg)

    if (numParams := len(inspect.signature(function).parameters)) > 1:
        result: list[Any] = pool.starmap(func=function, iterable=args, chunksize=chunkSize)
    elif numParams == 1:
        result = pool.map(func=function, iterable=args, chunksize=chunkSize)
    else:
        _result: list[multiprocessing.pool.ApplyResult] = [pool.apply_async(func=function) for __ in range(len(args))]
        result = [item.get() for item in _result]
    return result


def _flexibleMapTQDM(
    *,
    pool: multiprocessing.pool.Pool | multiprocessing.pool.ThreadPool,
    function: Callable[..., Any],
    args: Sequence[Any] | Sequence[Sequence[Any]],
    chunkSize: int | None,
    description: str | None = None,
) -> list[Any]:
    """Automatically determine the appropriate map type for a function and process arguments in TQDM parallelisms.

    Parameters
    ----------
    pool: multiprocessing.pool.Pool | multiprocessing.pool.ThreadPool
        The pool or threadpool whose workers are used for parallel processing.
    function: Callable[..., Any]
        The function to run in parallel.
    args: Sequence[Any] | Sequence[Sequence[Any]]
        A sequence of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of a sequence of sequences.
        If the function requires no parameters, the length of the sequence determines the number of function executions.
    chunkSize: int
        The number of function executions on the sequence to pass to each process.
    description: str | None
        If present, sets the string to display on the TQDM progress bar.

    Returns:
    -------
    list[Any]
        The outputs of the specified function across the sequence, in the provided order.

    Raises:
    ------
    TypeError
        If a generator function is provided as 'function' a TypeError is raised.
        Generators are unsupported as parallelization requires knowledge of their internal state.
    """
    # Generators are unsupported as their internal state must be known to parallelize calls to them
    # which would negate the purpose of calling the generator in the first place.
    # See https://stackoverflow.com/questions/7972295/python-generator-unpack-entire-generator-in-parallel
    if inspect.isgeneratorfunction(function):
        msg: str = "Generator functions are intentionally unsupported."
        raise TypeError(msg)

    if (numParams := len(inspect.signature(function).parameters)) > 1:
        result: list[Any] = list(
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
    elif numParams == 1:
        result = list(
            tqdm.tqdm(
                pool.imap(func=function, iterable=args, chunksize=chunkSize),
                total=len(args),
                desc=description,
            )
        )
    else:
        _result: list[multiprocessing.pool.ApplyResult] = list(
            tqdm.tqdm(
                (pool.apply_async(func=function) for __ in range(len(args))),
                total=len(args),
                desc=description,
            )
        )
        result = [item.get() for item in _result]
    return result
