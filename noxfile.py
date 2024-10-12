import os
import tempfile
from typing import NamedTuple

import nox


class WorkspacePackage(NamedTuple):
    name: str
    path: os.PathLike[str] | str


def install_package(session: nox.Session, package: WorkspacePackage) -> None:
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "uv",
            "export",
            "--package",
            package.name,
            "--no-hashes",
            "--frozen",
            "--output-file",
            requirements.name,
        )
        session.install("-r", requirements.name)


def install_dev(session: nox.Session) -> None:
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "uv",
            "export",
            "--only-dev",
            "--no-hashes",
            "--frozen",
            "--output-file",
            requirements.name,
        )
        session.install("-r", requirements.name)


packages = [
    nox.param(pkg, id=pkg.name)
    for pkg in [
        WorkspacePackage("myapp-pkg", "packages/myapp-pkg"),
        WorkspacePackage("myapp-invalid", "packages/myapp-invalid"),
    ]
]
nox.options.default_venv_backend = "uv"


@nox.session
@nox.parametrize("package", packages)
def type_check(session: nox.Session, package: WorkspacePackage) -> None:
    install_package(session, package)
    install_dev(session)

    session.run("mypy", package.path)


# @nox.session
# @nox.parametrize("package", packages)
# def test(session: nox.Session, package: WorkspacePackage) -> None:
#     install_package(session, package)
#     install_dev(session)

#     session.run("pytest", package.path)


@nox.session
def lint(session: nox.Session) -> None:
    install_dev(session)
    session.run("ruff", "check")
