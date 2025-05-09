"""pytest suite for basicParallelize

Includes tests for equivalency to serial execution in class TestOutputEquivalency.
Includes tests for branch points in class TestBranchPoints.
Includes tests for known errors and warnings in class TestKnownFailStates.
"""

import pytest

from basicParallelize import multiThread
from basicParallelize import multiThreadTQDM
from basicParallelize import parallelProcess
from basicParallelize import parallelProcessTQDM

# Constant Inputs for Output Equivalency Testing
ARGSONEARGFUNCTION = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
]
ARGSTWOARGFUNCTION = [
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
]

# Constant Outputs for Output Equivalency Testing
OUTPUTONEARGFUNCTION = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
OUTPUTTWOARGFUNCTION = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]


# Global Functions for Output Equivalency Testing
def oneArgFunction(x):
    return x**2


def twoArgFunction(x, y):
    return x + y


class TestOutputEquivalency:
    """Tests all function variants for equivalency to serial computation."""

    def test_multiThreadOneArg(self):
        assert (
            multiThread(function=oneArgFunction, args=ARGSONEARGFUNCTION)
            == OUTPUTONEARGFUNCTION
        )

    def test_multiThreadTwoArgs(self):
        assert (
            multiThread(function=twoArgFunction, args=ARGSTWOARGFUNCTION)
            == OUTPUTTWOARGFUNCTION
        )

    def test_multiThreadTQDMOneArg(self):
        assert (
            multiThreadTQDM(function=oneArgFunction, args=ARGSONEARGFUNCTION)
            == OUTPUTONEARGFUNCTION
        )

    def test_multiThreadTQDMTwoArgs(self):
        assert (
            multiThreadTQDM(function=twoArgFunction, args=ARGSTWOARGFUNCTION)
            == OUTPUTTWOARGFUNCTION
        )

    def test_parallelProcessOneArg(self):
        assert (
            parallelProcess(function=oneArgFunction, args=ARGSONEARGFUNCTION)
            == OUTPUTONEARGFUNCTION
        )

    def test_parallelProcessTwoArgs(self):
        assert (
            parallelProcess(function=twoArgFunction, args=ARGSTWOARGFUNCTION)
            == OUTPUTTWOARGFUNCTION
        )

    def test_parallelProcessTQDMOneArg(self):
        assert (
            parallelProcessTQDM(function=oneArgFunction, args=ARGSONEARGFUNCTION)
            == OUTPUTONEARGFUNCTION
        )

    def test_parallelProcessTQDMTwoArgs(self):
        assert (
            parallelProcessTQDM(function=twoArgFunction, args=ARGSTWOARGFUNCTION)
            == OUTPUTTWOARGFUNCTION
        )


class TestBranchPoints:
    """Ensures that all branch points are reached."""

    def test_setnJobsoverrideCPUCountIsFalse(self):
        """Confirms that nJobs can be set without errors while overrideCPUCount is False."""
        multiThread(
            function=oneArgFunction,
            args=ARGSONEARGFUNCTION,
            nJobs=2,
            overrideCPUCount=False,
        )
        multiThread(
            function=twoArgFunction,
            args=ARGSTWOARGFUNCTION,
            nJobs=2,
            overrideCPUCount=False,
        )
        multiThreadTQDM(
            function=oneArgFunction,
            args=ARGSONEARGFUNCTION,
            nJobs=2,
            overrideCPUCount=False,
        )
        multiThreadTQDM(
            function=twoArgFunction,
            args=ARGSTWOARGFUNCTION,
            nJobs=2,
            overrideCPUCount=False,
        )
        parallelProcess(
            function=oneArgFunction,
            args=ARGSONEARGFUNCTION,
            nJobs=2,
            overrideCPUCount=False,
        )
        parallelProcess(
            function=twoArgFunction,
            args=ARGSTWOARGFUNCTION,
            nJobs=2,
            overrideCPUCount=False,
        )
        parallelProcessTQDM(
            function=oneArgFunction,
            args=ARGSONEARGFUNCTION,
            nJobs=2,
            overrideCPUCount=False,
        )
        parallelProcessTQDM(
            function=twoArgFunction,
            args=ARGSTWOARGFUNCTION,
            nJobs=2,
            overrideCPUCount=False,
        )

    def test_setnJobsoverrideCPUCountIsTrue(self):
        """Confirms that nJobs can be set without errors while overrideCPUCount is True."""
        multiThread(
            function=oneArgFunction,
            args=ARGSONEARGFUNCTION,
            nJobs=2,
            overrideCPUCount=True,
        )
        multiThread(
            function=twoArgFunction,
            args=ARGSTWOARGFUNCTION,
            nJobs=2,
            overrideCPUCount=True,
        )
        multiThreadTQDM(
            function=oneArgFunction,
            args=ARGSONEARGFUNCTION,
            nJobs=2,
            overrideCPUCount=True,
        )
        multiThreadTQDM(
            function=twoArgFunction,
            args=ARGSTWOARGFUNCTION,
            nJobs=2,
            overrideCPUCount=True,
        )
        parallelProcess(
            function=oneArgFunction,
            args=ARGSONEARGFUNCTION,
            nJobs=2,
            overrideCPUCount=True,
        )
        parallelProcess(
            function=twoArgFunction,
            args=ARGSTWOARGFUNCTION,
            nJobs=2,
            overrideCPUCount=True,
        )
        parallelProcessTQDM(
            function=oneArgFunction,
            args=ARGSONEARGFUNCTION,
            nJobs=2,
            overrideCPUCount=True,
        )
        parallelProcessTQDM(
            function=twoArgFunction,
            args=ARGSTWOARGFUNCTION,
            nJobs=2,
            overrideCPUCount=True,
        )

    def test_setchunkSize(self):
        """Confirms that chunk sizes can be set without errors."""
        multiThread(function=oneArgFunction, args=ARGSONEARGFUNCTION, chunkSize=1)
        multiThread(function=twoArgFunction, args=ARGSTWOARGFUNCTION, chunkSize=1)
        multiThreadTQDM(function=oneArgFunction, args=ARGSONEARGFUNCTION, chunkSize=1)
        multiThreadTQDM(function=twoArgFunction, args=ARGSTWOARGFUNCTION, chunkSize=1)
        parallelProcess(function=oneArgFunction, args=ARGSONEARGFUNCTION, chunkSize=1)
        parallelProcess(function=twoArgFunction, args=ARGSTWOARGFUNCTION, chunkSize=1)
        parallelProcessTQDM(
            function=oneArgFunction, args=ARGSONEARGFUNCTION, chunkSize=1
        )
        parallelProcessTQDM(
            function=twoArgFunction, args=ARGSTWOARGFUNCTION, chunkSize=1
        )

    def test_autochunkSizeWithExtra(self):
        """Confirms that chunk sizes can be left to default values when args don't divide evenly."""
        multiThread(function=oneArgFunction, args=ARGSONEARGFUNCTION)
        multiThread(function=twoArgFunction, args=ARGSTWOARGFUNCTION)
        multiThreadTQDM(function=oneArgFunction, args=ARGSONEARGFUNCTION)
        multiThreadTQDM(function=twoArgFunction, args=ARGSTWOARGFUNCTION)
        parallelProcess(function=oneArgFunction, args=ARGSONEARGFUNCTION)
        parallelProcess(function=twoArgFunction, args=ARGSTWOARGFUNCTION)
        parallelProcessTQDM(function=oneArgFunction, args=ARGSONEARGFUNCTION)
        parallelProcessTQDM(function=twoArgFunction, args=ARGSTWOARGFUNCTION)

    def test_autochunkSizeNoExtra(self):
        """Confirms that chunk sizes can be left to default values when args divide evenly."""
        multiThread(function=oneArgFunction, args=ARGSONEARGFUNCTION[:8], nJobs=2)
        multiThread(function=twoArgFunction, args=ARGSTWOARGFUNCTION[:8], nJobs=2)
        multiThreadTQDM(function=oneArgFunction, args=ARGSONEARGFUNCTION[:8], nJobs=2)
        multiThreadTQDM(function=twoArgFunction, args=ARGSTWOARGFUNCTION[:8], nJobs=2)
        parallelProcess(function=oneArgFunction, args=ARGSONEARGFUNCTION[:8], nJobs=2)
        parallelProcess(function=twoArgFunction, args=ARGSTWOARGFUNCTION[:8], nJobs=2)
        parallelProcessTQDM(
            function=oneArgFunction, args=ARGSONEARGFUNCTION[:8], nJobs=2
        )
        parallelProcessTQDM(
            function=twoArgFunction, args=ARGSTWOARGFUNCTION[:8], nJobs=2
        )


class TestKnownFailStates:
    """Tests for known failure states and warnings:

    The following failure states are known:
        TypeError: Attempting to pass an incorrect number of arguments to a function.
        AttrributeError: Attempting to pass a local function to a process pool.
    The following warnings are known:
        RunTimeWarning: Setting overrideCPUCount to True while nJobs is unset.
    """

    def test_TypeErrorTwoArgsToOneArgFunction(self):
        """Confirms that one argument functions don't accept multiple arguments."""
        with pytest.raises(TypeError):
            multiThread(function=oneArgFunction, args=ARGSTWOARGFUNCTION)
        with pytest.raises(TypeError):
            multiThreadTQDM(function=oneArgFunction, args=ARGSTWOARGFUNCTION)
        with pytest.raises(TypeError):
            parallelProcess(function=oneArgFunction, args=ARGSTWOARGFUNCTION)
        with pytest.raises(TypeError):
            parallelProcessTQDM(function=oneArgFunction, args=ARGSTWOARGFUNCTION)

    def test_TypeErrorOneArgToTwoArgFunction(self):
        """Confirms that multi argument functions don't accept only one argument."""
        with pytest.raises(TypeError):
            multiThread(twoArgFunction, args=ARGSONEARGFUNCTION)
        with pytest.raises(TypeError):
            multiThreadTQDM(twoArgFunction, args=ARGSONEARGFUNCTION)
        with pytest.raises(TypeError):
            parallelProcess(twoArgFunction, args=ARGSONEARGFUNCTION)
        with pytest.raises(TypeError):
            parallelProcessTQDM(twoArgFunction, args=ARGSONEARGFUNCTION)

    def test_LocalFunctions(self):
        """Confirms that local functions can be safely passed to thread pools.
        Also confirms that local functions fail to pickle and thus aren't passed to process pools.
        """

        def localOneArgFunction(x):
            pass

        def localTwoArgFunction(x, y):
            pass

        multiThread(function=localOneArgFunction, args=ARGSONEARGFUNCTION)
        multiThread(function=localTwoArgFunction, args=ARGSTWOARGFUNCTION)
        multiThreadTQDM(function=localOneArgFunction, args=ARGSONEARGFUNCTION)
        multiThreadTQDM(function=localTwoArgFunction, args=ARGSTWOARGFUNCTION)
        with pytest.raises(AttributeError):
            parallelProcess(localOneArgFunction, args=ARGSONEARGFUNCTION)
        with pytest.raises(AttributeError):
            parallelProcess(localTwoArgFunction, args=ARGSTWOARGFUNCTION)
        with pytest.raises(AttributeError):
            parallelProcessTQDM(localOneArgFunction, args=ARGSONEARGFUNCTION)
        with pytest.raises(AttributeError):
            parallelProcessTQDM(localTwoArgFunction, args=ARGSTWOARGFUNCTION)

    def test_unsetnJobsoverrideCPUCountIsTrue(self):
        """Confirms that a warning is raised if nJobs is unset while overrideCPUCount is True."""
        with pytest.warns(RuntimeWarning):
            multiThread(
                function=oneArgFunction, args=ARGSONEARGFUNCTION, overrideCPUCount=True
            )
        with pytest.warns(RuntimeWarning):
            multiThread(
                function=twoArgFunction, args=ARGSTWOARGFUNCTION, overrideCPUCount=True
            )
        with pytest.warns(RuntimeWarning):
            multiThreadTQDM(
                function=oneArgFunction, args=ARGSONEARGFUNCTION, overrideCPUCount=True
            )
        with pytest.warns(RuntimeWarning):
            multiThreadTQDM(
                function=twoArgFunction, args=ARGSTWOARGFUNCTION, overrideCPUCount=True
            )
        with pytest.warns(RuntimeWarning):
            parallelProcess(
                function=oneArgFunction, args=ARGSONEARGFUNCTION, overrideCPUCount=True
            )
        with pytest.warns(RuntimeWarning):
            parallelProcess(
                function=twoArgFunction, args=ARGSTWOARGFUNCTION, overrideCPUCount=True
            )
        with pytest.warns(RuntimeWarning):
            parallelProcessTQDM(
                function=oneArgFunction, args=ARGSONEARGFUNCTION, overrideCPUCount=True
            )
        with pytest.warns(RuntimeWarning):
            parallelProcessTQDM(
                function=twoArgFunction, args=ARGSTWOARGFUNCTION, overrideCPUCount=True
            )
