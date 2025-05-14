import nox

nox.options.sessions = ["lint", "coverageTestsReport"]


@nox.session(reuse_venv=False)
def lint(session) -> None:
    session.install(".")
    session.install("ruff")
    session.install("pylint")
    session.run(
        "ruff",
        "check",
        "--fix",
    )
    session.run(
        "ruff",
        "format",
    )
    (
        session.run(
            "ruff",
            "clean",
        ),
    )
    session.run("pylint", "./src/basicParallelize")


@nox.session(
    python=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"],
    reuse_venv=False,
)
def coverageTestsReport(session) -> None:
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
    )
    session.run(
        "coverage",
        "report",
        "-m",
    )


@nox.session(reuse_venv=False)
def genbadge(session) -> None:
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

@nox.session(reuse_venv=False)
def release(session) -> None:
    session.install("build")
    session.install("twine")
    session.run("python","-m","build")
    session.run("python","-m", "twine", "upload", "dist/*")
    session.run("rm", "dist/*")
