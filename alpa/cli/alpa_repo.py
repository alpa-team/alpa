"""
These commands need GH API token.
"""


from os import getcwd
from pathlib import Path

import click

from alpa.repository import AlpaRepo


pkg_name = click.argument("name", type=str)


@click.command("create")
@pkg_name
def create(name: str) -> None:
    """Create new package"""
    AlpaRepo(Path(getcwd())).create_package(name)


@click.command("delete")
@pkg_name
def delete(name: str) -> None:
    """Delete existing package"""
    pass


@click.command("request-package")
@pkg_name
def request_package(name: str) -> None:
    """Request new branch for new package in upstream"""
    AlpaRepo(Path(getcwd())).request_package(name)
