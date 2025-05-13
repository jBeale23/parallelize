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
ARGSZEROARGFUNCTION = range(11)
ARGSONEARGFUNCTION = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
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


# Global Functions for Output Equivalency Testing
def zeroArgFunction() -> int:
    return 1


def oneArgFunction(x: int) -> int:
    return x**2


def twoArgFunction(x: int, y: int) -> int:
    return x + y


# Serial Outputs for Output Equivalency Testing
OUTPUTZEROARGFUNCTION = [zeroArgFunction() for __ in ARGSZEROARGFUNCTION]
OUTPUTONEARGFUNCTION = [oneArgFunction(i) for i in ARGSONEARGFUNCTION]
OUTPUTTWOARGFUNCTION = [twoArgFunction(*i) for i in ARGSTWOARGFUNCTION]


# Metafunction for parametrizing tests
def pytest_generate_tests(metafunc):
    if "threading" in metafunc.fixturenames:
        metafunc.parametrize("threading", [multiThread, multiThreadTQDM])
    if "processes" in metafunc.fixturenames:
        metafunc.parametrize("processes", [parallelProcess, parallelProcessTQDM])
    if "parallelism" in metafunc.fixturenames:
        metafunc.parametrize(
            "parallelism",
            [multiThread, multiThreadTQDM, parallelProcess, parallelProcessTQDM],
        )
    if "function" in metafunc.fixturenames:
        metafunc.parametrize(
            "function, args, output",
            [
                (zeroArgFunction, ARGSZEROARGFUNCTION, OUTPUTZEROARGFUNCTION),
                (oneArgFunction, ARGSONEARGFUNCTION, OUTPUTONEARGFUNCTION),
                (twoArgFunction, ARGSTWOARGFUNCTION, OUTPUTTWOARGFUNCTION),
            ],
        )


class TestOutputEquivalency:
    """Tests all function variants for equivalency to serial computation."""

    def test_outPutEquivalency(self, parallelism, function, args, output):
        assert parallelism(function=function, args=args) == output


class TestBranchPoints:
    """Ensures that all branch points are reached."""

    def test_setnJobsoverrideCPUCountIsFalse(self, parallelism, function, args, output):
        """Confirms that nJobs can be set without errors while overrideCPUCount is False."""
        assert (
            parallelism(
                function=function,
                args=args,
                nJobs=2,
                overrideCPUCount=False,
            )
            == output
        )

    def test_setnJobsoverrideCPUCountIsTrue(self, parallelism, function, args, output):
        """Confirms that nJobs can be set without errors while overrideCPUCount is True."""
        assert (
            parallelism(
                function=function,
                args=args,
                nJobs=2,
                overrideCPUCount=True,
            )
            == output
        )

    def test_setchunkSize(self, parallelism, function, args, output):
        """Confirms that chunk sizes can be set without errors."""
        if function != zeroArgFunction:
            assert parallelism(function=function, args=args, chunkSize=1) == output

    def test_autochunkSizeWithExtra(self, parallelism, function, args, output):
        """Confirms that chunk sizes can be left to default values when args don't divide evenly."""
        assert parallelism(function=function, args=args) == output

    def test_autochunkSizeNoExtra(self, parallelism, function, args, output):
        """Confirms that chunk sizes can be left to default values when args divide evenly."""
        assert parallelism(function=function, args=args[:8], nJobs=2) == output[:8]


class TestKnownFailStates:
    """Tests for known failure states and warnings:

    The following failure states are known:
        TypeError: Attempting to pass an incorrect number of arguments to a function.
        AttrributeError: Attempting to pass a local function to a process pool.
    The following warnings are known:
        UserWarning: Setting overrideCPUCount to True while nJobs is unset.
    """

    def test_TypeErrorTwoArgsToOneArgFunction(self, parallelism):
        """Confirms that one argument functions don't accept multiple arguments."""
        with pytest.raises(TypeError):
            parallelism(function=oneArgFunction, args=ARGSTWOARGFUNCTION)

    def test_TypeErrorOneArgToTwoArgFunction(self, parallelism):
        """Confirms that multi argument functions don't accept only one argument."""
        with pytest.raises(TypeError):
            parallelism(function=twoArgFunction, args=ARGSONEARGFUNCTION)

    def test_LocalZeroArgFunctionThreads(self, threading):
        """Confirms that local zero arg functions can be safely passed to thread pools."""

        def localZeroArgFunction():
            pass

        threading(function=localZeroArgFunction, args=ARGSZEROARGFUNCTION)

    def test_LocalOneArgFunctionThreads(self, threading):
        """Confirms that local one arg functions can be safely passed to thread pools."""

        def localOneArgFunction(x):
            pass

        threading(function=localOneArgFunction, args=ARGSONEARGFUNCTION)

    def test_LocalTwoArgFunctionThreads(self, threading):
        """Confirms that local two arg functions can be safely passed to thread pools."""

        def localTwoArgFunction(x, y):
            pass

        threading(function=localTwoArgFunction, args=ARGSTWOARGFUNCTION)

    def test_LocalZeroArgFunctionProcesses(self, processes):
        """Confirms that local zero arg functions fail to pickle and thus aren't passed to process pools."""

        def localZeroArgFunction():  # pragma: no cover
            # Processes fail to pickle local functions and thus this code is never reached
            pass

        with pytest.raises(AttributeError):
            processes(function=localZeroArgFunction, args=ARGSZEROARGFUNCTION)

    def test_LocalOneArgFunctionProcesses(self, processes):
        """Confirms that local one arg functions fail to pickle and thus aren't passed to process pools."""

        def localOneArgFunction(x):  # pragma: no cover
            # Processes fail to pickle local functions and thus this code is never reached
            pass

        with pytest.raises(AttributeError):
            processes(localOneArgFunction, args=ARGSONEARGFUNCTION)

    def test_LocalTwoArgFunctionProcesses(self, processes):
        """Confirms that local two arg functions fail to pickle and thus aren't passed to process pools."""

        def localTwoArgFunction(x, y):  # pragma: no cover
            # Processes fail to pickle local functions and thus this code is never reached
            pass

        with pytest.raises(AttributeError):
            processes(localTwoArgFunction, args=ARGSTWOARGFUNCTION)

    def test_unsetnJobsoverrideCPUCountIsTrue(
        self, parallelism, function, args, output
    ):
        """Confirms that a warning is raised if nJobs is unset while overrideCPUCount is True."""
        with pytest.warns(UserWarning):
            assert (
                parallelism(function=function, args=args, overrideCPUCount=True)
                == output
            )

    def test_chunkSizeWithZeroArgFunction(self, parallelism, function, args, output):
        """Confirms that a warning is raised if chunkSize is set for a 0 argument function."""
        if function == zeroArgFunction:
            with pytest.warns(UserWarning):
                assert parallelism(function=function, args=args, chunkSize=1) == output
