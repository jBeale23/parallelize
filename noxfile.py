"""Nox configuration for basicParallelize."""

import argparse

import nox

nox.options.sessions = ["lint", "test"]


@nox.session(reuse_venv=False)
def lint(session: nox.Session) -> None:
    """Automatically lints the repository using ruff."""
    session.install(".")
    session.install("ruff")
    session.install("pytest")
    session.run("ruff", "check", "--fix")
    session.run(
        "ruff",
        "format",
    )
    session.run(
        "ruff",
        "clean",
    )


@nox.session(
    requires=["lint"],
    python=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"],
    reuse_venv=False,
)
def test(session: nox.Session) -> None:
    """Automatically tests the repository and determines coverage for Python 3.8+."""
    session.install(".")
    session.install("coverage")
    session.install("pytest")
    session.run(
        "coverage",
        "run",
        "--branch",
        "--module",
        "pytest",
        "--verbose",
        "-ra",
        "--strict-markers",
        "tests/testParallelize.py",
    )
    session.run(
        "coverage",
        "report",
        "-m",
    )


@nox.session(requires=["lint"], reuse_venv=False)
def genbadge(session: nox.Session) -> None:
    """Generates coverage and test badges."""
    session.install(".")
    session.install("coverage")
    session.install("pytest")
    session.install("genbadge[all]")
    session.run(
        "coverage",
        "run",
        "--branch",
        "--module",
        "pytest",
        "--verbose",
        "-ra",
        "--strict-markers",
        "--junit-xml=reports/tests/junit.xml",
        "tests/testParallelize.py",
    )
    session.run(
        "coverage",
        "xml",
        "-o",
        "reports/coverage/coverage.xml",
    )
    session.run(
        "genbadge",
        "tests",
        "--input-file=reports/tests/junit.xml",
        "--output-file=reports/tests/tests-badge.svg",
    )
    session.run(
        "genbadge",
        "coverage",
        "--input-file=reports/coverage/coverage.xml",
        "--output-file=reports/coverage/coverage-badge.svg",
    )


@nox.session(reuse_venv=True)
def updateDev(session: nox.Session) -> None:
    """Automates release process for the dev branch.

    Invokes bump-my-version with the posarg setting the version.

    Usage:
        $ nox -s updateDev -- [major|minor|patch]
    """
    parser = argparse.ArgumentParser(description="Release a semver version.")
    parser.add_argument(
        "version",
        type=str,
        nargs=1,
        help="The type of semver release to make.",
        choices={"major", "minor", "patch"},
    )
    args: argparse.Namespace = parser.parse_args(args=session.posargs)
    version: str = args.version.pop()

    confirm: str = input(f"You are about to bump the {version!r} version. Are you sure? [y/n]: ")

    if confirm.lower().strip() != "y":
        session.error(f"You said no when prompted to bump the {version!r} version.")

    session.log(f"Bumping the {version!r} version")
    session.install("bump-my-version")
    session.run("bump-my-version", "bump", version)
    session.run("git", "push", external=True)
