"""Nox sessions."""
import os
import tempfile
from typing import Any

import nox
from nox.sessions import Session
from nox_poetry import session

"""Nox sessions."""

# Disabling tests as free version is generating errors
nox.options.sessions = ("lint", "tests", "mypy", "pytype")

locations = "src", "tests", "noxfile.py", "docs/conf.py"

package = "hm_python"


# Handle dependencies using poetry and constraints files
def install_with_constraints(session: Session, *args: str, **kwargs: Any) -> None:
    """Install packages constrained by Poetry's lock file."""
    with tempfile.NamedTemporaryFile(delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=constraints.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)
        requirements.close()
        os.unlink(requirements.name)


@nox.session(python=["3.10"])
def tests(session: Session) -> None:
    """Run the test suite."""
    # To run a specific test, ex. nox -- tests/test_console.py
    # To run a specific function based on name matching, "pytest -k <func name substr>"
    # To do this with nox, "nox -rs tests -- -k <func name substr, ex. test_init>"
    # This passes anything after args into posargs (ex. -k test_init) so that you can
    #   run a specific test at once. For example, "nox -rs tests -- -k test init" does
    #   "pytest -k test_init"
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock", "mock"
    )
    session.run("pytest", *args)


@nox.session(python=["3.10"])
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    # black gives warnings if it detects that black would reformat source files
    # import-order states that imports should be grouped by:
    #     Standard library
    #     Third party packages
    #     Local packages
    # bugbear helps to find various bugs and design problems in programs
    # bandit finds common security issues in Python code

    install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
    )
    session.run("flake8", *args)


@nox.session(python="3.10")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@session(python="3.10")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["src", "tests"]
    session.install(".")
    install_with_constraints(session, "mypy")
    session.run("mypy", *args)


@nox.session(python="3.10")
def pytype(session: Session) -> None:
    """Type-check using pytype."""
    args = session.posargs or ["--disable=import-error", *locations]
    install_with_constraints(session, "pytype")
    session.run("pytype", *args)


@nox.session(python="3.10")
def typeguard(session: Session) -> None:
    """Runtime type checking using Typeguard."""
    args = session.posargs or ["-m", "not e2e"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "pytest", "pytest-mock", "typeguard")
    session.run("pytest", f"--typeguard-packages={package}", *args)


@nox.session(python=False)
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("python", "-m", "xdoctest", package, *args)


@nox.session(python="3.10")
def docs(session: Session) -> None:
    """Build the documentation."""
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "sphinx", "sphinx-autodoc-typehints")
    session.run("sphinx-build", "docs", "docs/_build")
