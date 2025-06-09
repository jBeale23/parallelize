"""pytest suite for basicParallelize.

Includes tests for branch points in class TestBranchPoints.
Includes tests for methods in class TestClassAndInstanceMethods
Includes tests for known errors and warnings in class TestKnownFailStates.
"""

from __future__ import annotations

from typing import Any, Generator, Literal, NoReturn

import pytest

from basicParallelize import (
    multiThread,
    multiThreadTQDM,
    parallelProcess,
    parallelProcessTQDM,
)

# Constant Inputs for Output Equivalency Testing
ARGSZEROARGFUNCTION = range(11)
ARGSONEARGFUNCTION: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ARGSTWOARGFUNCTION: list[tuple[int, int]] = [
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
    """An example zero argument function that always returns 1."""
    return 1


def oneArgFunction(x: int) -> int:
    """An example one argument function that squares its input."""
    return x**2


def twoArgFunction(x: int, y: int) -> int:
    """An example two argument function that sums its inputs."""
    return x + y


class MethodsTestClass:
    """A class containing methods for testing parallelisms."""

    SomeClassData: int = 0

    def __init__(self, parameter: int) -> None:
        """Instantiates a MethodsTestClass with some trivial parameter."""
        self.parameter = parameter
        MethodsTestClass.SomeClassData += 1

    def returnParameter(self) -> int:
        """Retrieves the trivial parameter of an instance of MethodsTestClass."""
        return self.parameter

    @classmethod
    def retrieveInstanceCount(cls) -> int:
        """Retrieves the current count of instances of the MethodsTestClass."""
        return cls.SomeClassData

    @staticmethod
    def zeroArgStaticMethod() -> int:
        """An example zero argument method that always returns 1."""
        return 1

    @staticmethod
    def oneArgStaticMethod(x: int) -> int:
        """An example one argument method that squares its input."""
        return x**2

    @staticmethod
    def twoArgStaticMethod(x: int, y: int) -> int:
        """An example two argument method that sums its inputs."""
        return x + y


# Global Generator Functions for Known Failure Testing
def zeroArgGenerator() -> Generator[int, Any, NoReturn]:  # pragma: no cover
    # Generator functions are intentionally unsupported and thus will never be executed.
    """An example zero argument generator that yields an infinite sequence."""
    num = 0
    while True:
        yield num
        num += 1


def oneArgGenerator(limit: int) -> Generator[int, Any, None]:  # pragma: no cover
    # Generator functions are not supported and thus will never be executed.
    """An example one argument generator that yields the highest fibonnaci value below the limit."""
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b


def twoArgGenerator(start: int, end: int) -> Generator[int, Any, None]:  # pragma: no cover
    # Generator functions are not supported and thus will never be executed.
    """An example two argument generator that yields numbers within a specified range."""
    while start <= end:
        yield start
        start += 1


# Serial Outputs for Output Equivalency Testing
OUTPUTZEROARGFUNCTION: list[int] = [zeroArgFunction() for __ in ARGSZEROARGFUNCTION]
OUTPUTONEARGFUNCTION: list[int] = [oneArgFunction(i) for i in ARGSONEARGFUNCTION]
OUTPUTTWOARGFUNCTION: list[int] = [twoArgFunction(*i) for i in ARGSTWOARGFUNCTION]


def pytest_generate_tests(metafunc) -> None:
    """Metafunction to automate parameterization of tests."""
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
    if "chunkableFunction" in metafunc.fixturenames:
        metafunc.parametrize(
            "chunkableFunction, args, output",
            [
                (oneArgFunction, ARGSONEARGFUNCTION, OUTPUTONEARGFUNCTION),
                (twoArgFunction, ARGSTWOARGFUNCTION, OUTPUTTWOARGFUNCTION),
            ],
        )

    if "generator" in metafunc.fixturenames:
        metafunc.parametrize(
            "generator, args",
            [
                (zeroArgGenerator, ARGSZEROARGFUNCTION),
                (oneArgGenerator, ARGSONEARGFUNCTION),
                (twoArgGenerator, ARGSTWOARGFUNCTION),
            ],
        )
    if "staticMethod" in metafunc.fixturenames:
        metafunc.parametrize(
            "staticMethod, args, output",
            [
                (MethodsTestClass.zeroArgStaticMethod, ARGSZEROARGFUNCTION, OUTPUTZEROARGFUNCTION),
                (MethodsTestClass.oneArgStaticMethod, ARGSONEARGFUNCTION, OUTPUTONEARGFUNCTION),
                (MethodsTestClass.twoArgStaticMethod, ARGSTWOARGFUNCTION, OUTPUTTWOARGFUNCTION),
            ],
        )


class TestOutputEquivalency:
    """Tests all parallelism variants for equivalency to serial computation."""

    def testOutPutEquivalencyFunctions(self, parallelism, function, args, output) -> None:
        """Tests output equivalency to serial computation of functions."""
        assert parallelism(function=function, args=args) == output

    def testOutPutEquivalencyStaticMethods(self, parallelism, staticMethod, args, output) -> None:
        """Tests output equivalency to serial computation of static methods."""
        assert parallelism(function=staticMethod, args=args) == output


class TestClassAndInstanceMethods:
    """Tests all parallelism variants with class and instance methods."""

    InstanceOfMethodsTestClass = MethodsTestClass(1)

    def testInstanceMethod(self, parallelism) -> None:
        """Tests that instance methods can be used with parallelisms."""
        assert parallelism(self.InstanceOfMethodsTestClass.returnParameter, ARGSZEROARGFUNCTION) == [
            1 for __ in ARGSZEROARGFUNCTION
        ]

    def testClassMethod(self, parallelism) -> None:
        """Tests that class methods can be used with parallelisms."""
        assert parallelism(MethodsTestClass.retrieveInstanceCount, ARGSZEROARGFUNCTION) == [
            1 for __ in ARGSZEROARGFUNCTION
        ]


class TestBranchPoints:
    """Ensures that all branch points are reached."""

    def testSetnJobsoverrideCPUCountIsFalse(self, parallelism, function, args, output) -> None:
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

    def testSetnJobsoverrideCPUCountIsTrue(self, parallelism, function, args, output) -> None:
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

    def testSetChunkSize(self, parallelism, chunkableFunction, args, output) -> None:
        """Confirms that chunk sizes can be set without errors."""
        assert parallelism(function=chunkableFunction, args=args, chunkSize=1) == output

    def testAutoChunkSizeWithExtra(self, parallelism, function, args, output) -> None:
        """Confirms that chunk sizes can be left to default values when args don't divide evenly."""
        assert parallelism(function=function, args=args) == output

    def testAutoChunkSizeNoExtra(self, parallelism, function, args, output) -> None:
        """Confirms that chunk sizes can be left to default values when args divide evenly."""
        assert parallelism(function=function, args=args[:8], nJobs=2) == output[:8]


class TestKnownFailStates:
    """Tests for known failure states and warnings.

    The following failure states are known:
        AttrributeError: Attempting to pass a local function to a process pool.
        TypeError: Attempting to pass a generator function to a parallelism.
        TypeError: Attempting to pass an incorrect number of arguments to a function.
    The following warnings are known:
        UserWarning: Setting overrideCPUCount to True while nJobs is unset.
        UserWarning: Specifying chunkSize while passing a function that requires no arguments.
    """

    def testTypeErrorTwoArgsToOneArgFunction(self, parallelism) -> None:
        """Confirms that one argument functions don't accept multiple arguments."""
        with pytest.raises(TypeError):
            parallelism(function=oneArgFunction, args=ARGSTWOARGFUNCTION)

    def testTypeErrorOneArgToTwoArgFunction(self, parallelism) -> None:
        """Confirms that multi argument functions don't accept only one argument."""
        with pytest.raises(TypeError):
            parallelism(function=twoArgFunction, args=ARGSONEARGFUNCTION)

    def testLocalZeroArgFunctionThreads(self, threading) -> None:
        """Confirms that local zero arg functions can be safely passed to thread pools."""

        def localZeroArgFunction() -> Literal[1]:
            return 1

        threading(function=localZeroArgFunction, args=ARGSZEROARGFUNCTION)

    def testLocalOneArgFunctionThreads(self, threading) -> None:
        """Confirms that local one arg functions can be safely passed to thread pools."""

        def localOneArgFunction(x: float) -> int | float:
            return x**2

        threading(function=localOneArgFunction, args=ARGSONEARGFUNCTION)

    def testLocalTwoArgFunctionThreads(self, threading) -> None:
        """Confirms that local two arg functions can be safely passed to thread pools."""

        def localTwoArgFunction(x: float, y: float) -> int | float:
            return x + y

        threading(function=localTwoArgFunction, args=ARGSTWOARGFUNCTION)

    def testLocalZeroArgFunctionProcesses(self, processes) -> None:
        """Confirms that local zero arg functions fail to pickle and thus aren't passed to process pools."""

        def localZeroArgFunction() -> None:  # pragma: no cover
            # Processes fail to pickle local functions and thus this code is never reached
            pass

        with pytest.raises(AttributeError):
            processes(function=localZeroArgFunction, args=ARGSZEROARGFUNCTION)

    def testLocalOneArgFunctionProcesses(self, processes) -> None:
        """Confirms that local one arg functions fail to pickle and thus aren't passed to process pools."""

        def localOneArgFunction(_x) -> None:  # pragma: no cover
            # Processes fail to pickle local functions and thus this code is never reached
            pass

        with pytest.raises(AttributeError):
            processes(function=localOneArgFunction, args=ARGSONEARGFUNCTION)

    def testLocalTwoArgFunctionProcesses(self, processes) -> None:
        """Confirms that local two arg functions fail to pickle and thus aren't passed to process pools."""

        def localTwoArgFunction(_x, _y) -> None:  # pragma: no cover
            # Processes fail to pickle local functions and thus this code is never reached
            pass

        with pytest.raises(AttributeError):
            processes(function=localTwoArgFunction, args=ARGSTWOARGFUNCTION)

    def testUnsetnJobsCverrideCPUCountIsTrue(self, parallelism, function, args, output) -> None:
        """Confirms that a warning is raised if nJobs is unset while overrideCPUCount is True."""
        with pytest.warns(UserWarning):
            assert parallelism(function=function, args=args, overrideCPUCount=True) == output

    def testChunkSizeWithZeroArgFunction(self, parallelism) -> None:
        """Confirms that a warning is raised if chunkSize is set for a 0 argument function."""
        with pytest.warns(UserWarning):
            assert parallelism(function=zeroArgFunction, args=ARGSZEROARGFUNCTION, chunkSize=1) == OUTPUTZEROARGFUNCTION

    def testTypeErrorGeneratorFunction(self, parallelism, generator, args) -> None:
        """Confirms that a TypeError is raised if a generator function is passed to a parallelism."""
        with pytest.raises(TypeError):
            parallelism(function=generator, args=args)
