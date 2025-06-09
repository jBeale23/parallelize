"""Wrappers for multiprocessing.Pool and multiprocessing.pool.ThreadPool with TQDM progress bar integration."""

from __future__ import annotations

import multiprocessing
import multiprocessing.pool
from typing import Any, Callable, Sequence

from ._helpers import _determineChunkSize, _determineNJobs, _flexibleMapTQDM


# PLR0913 Too-Many-Arguments warning is disabled as providing a single contact point for end users is the goal.
# Sensible defaults are provided to reduce mental burden while still allowing customization for advanced use.
def parallelProcessTQDM(  # noqa: PLR0913
    function: Callable[..., Any],
    args: Sequence[Any] | Sequence[Sequence[Any]],
    *,
    nJobs: int | None = None,
    chunkSize: int | None = None,
    overrideCPUCount: bool = False,
    description: str | None = None,
) -> list[Any]:
    """Creates a process pool to run a provided function on each element of a sequence with TQDM.

    Parameters
    ----------
    function: Callable[..., Any]
        The function to run in parallel.
    args: Sequence[Any] | Sequence[Sequence[Any]]
        A sequence of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of a sequence of sequences.
        If the function requires no parameters, the length of the sequence determines the number of function executions.
    nJobs: int | None
        The number of processes to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        If unspecified, defaults to system logical CPU count.
    chunkSize: int | None
        The number of function executions on the sequence to pass to each process.
        If unspecified, defaults to heuristic calculation of divmod(len(args), nJobs * 4).
    overrideCPUCount: bool
        If set to True, the user provided nJobs is used as the number of processes to start simultaneously.
        This is done regardless of system resources available or possible Windows errors.
        Defaults to False.
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
        They are intentionally unsupported as parallelization of calls to non trivial generators
        requires knowledge of the generator's internal state.

    Raises:
    ------
    TypeError
        If a generator function is provided as 'function' a TypeError is raised.
        They are intentionally unsupported as parallelization of calls to non trivial generators
        requires knowledge of the generator's internal state.

    Warnings:
    --------
    UserWarning
        If `chunkSize` is specified while `function` requires no parameters, a warning is issued to notify users that
        the specified `chunkSize` has no effect.
    UserWarning
        If `nJobs` is None while `overrideCPUCount` is True, a warning is issued to notify users that they
        may have forgotten to specify `nJobs` or unintentinally specified `overrideCPUCount`.
    """
    nJobs = _determineNJobs(nJobs=nJobs, overrideCPUCount=overrideCPUCount)

    chunkSize = _determineChunkSize(
        function=function,
        args=args,
        nJobs=nJobs,
        chunkSize=chunkSize,
    )

    with multiprocessing.Pool(processes=nJobs) as pool:
        result: list[Any] = _flexibleMapTQDM(
            pool=pool,
            function=function,
            args=args,
            chunkSize=chunkSize,
            description=description,
        )

    return result


# PLR0913 Too-Many-Arguments warning is disabled as providing a single contact point for end users is the goal.
# Sensible defaults are provided to reduce mental burden while still allowing customization for advanced use.
def multiThreadTQDM(  # noqa: PLR0913
    function: Callable[..., Any],
    args: Sequence[Any] | Sequence[Sequence[Any]],
    *,
    nJobs: int | None = None,
    chunkSize: int | None = None,
    overrideCPUCount: bool = False,
    description: str | None = None,
) -> list[Any]:
    """Creates a thread pool to run a provided function on each element of a sequence with TQDM.

    Parameters
    ----------
    function: Callable[..., Any]
        The function to run in parallel.
    args: Sequence[Any] | Sequence[Sequence[Any]]
        A sequence of parameters to pass to the function.
        If the function requires more than one parameter, they must be provided in the form of a sequence of sequences.
        If the function requires no parameters, the length of the sequence determines the number of function executions.
    nJobs: int | None
        The number of threads to start simultaneously.
        Capped by system CPU count and 61 to avoid bottlenecking and Windows errors respectively.
        If unspecified, defaults to system logical CPU count.
    chunkSize: int | None
        The number of function executions on the sequence to pass to each process.
        If unspecified, defaults to heuristic calculation of divmod(len(args), nJobs * 4).
    overrideCPUCount: bool
        If set to True, the user provided nJobs is used as the number of threads to start simultaneously.
        This is done regardless of system resources available or possible Windows errors.
        Defaults to False.
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
        They are intentionally unsupported as parallelization of calls to non trivial generators
        requires knowledge of the generator's internal state.

    Warnings:
    --------
    UserWarning
        If `chunkSize` is specified while `function` requires no parameters, a warning is issued to notify users that
        the specified `chunkSize` has no effect.
    UserWarning
        If `nJobs` is None while `overrideCPUCount` is True, a warning is issued to notify users that they
        may have forgotten to specify `nJobs` or unintentinally specified `overrideCPUCount`.
    """
    nJobs = _determineNJobs(nJobs=nJobs, overrideCPUCount=overrideCPUCount)

    chunkSize = _determineChunkSize(
        function=function,
        args=args,
        nJobs=nJobs,
        chunkSize=chunkSize,
    )

    with multiprocessing.pool.ThreadPool(processes=nJobs) as pool:
        result: list[Any] = _flexibleMapTQDM(
            pool=pool,
            function=function,
            args=args,
            chunkSize=chunkSize,
            description=description,
        )

    return result
