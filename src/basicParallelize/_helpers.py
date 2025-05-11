"""Helper functions for shared logic between _parallelize.py and _parallelizeTQDM.py."""

from __future__ import annotations
import multiprocessing
from typing import Any, Iterable
import warnings


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


def _determineChunkSize(
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
    # Used as a default to reduce worker overhead.
    # Consider specifying smaller chunk sizes for small datasets.
    # Alternatively, consider the heuristic calculation of math.ceil(len(args) / nJobs)) for large datasets.
    # See the below link for a discussion of the chosen default heuristic.
    # https://stackoverflow.com/questions/53751050/multiprocessing-understanding-logic-behind-chunksize
    if chunkSize is None:
        chunkSize, extra = divmod(len(args), nJobs * 4)
        if extra:
            chunkSize += 1
    return chunkSize
