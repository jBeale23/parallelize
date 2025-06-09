"""Wrappers for the multiprocessing module's Pool and ThreadPool classes, including support for TQDM."""

__all__ = ["multiThread", "multiThreadTQDM", "parallelProcess", "parallelProcessTQDM"]
__version__ = "1.1.2"
__author__ = "Joshua Beale <jbeale2023@gmail.com>"

from ._parallelize import multiThread, parallelProcess
from ._parallelizeTQDM import multiThreadTQDM, parallelProcessTQDM
