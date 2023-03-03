from os import getcwd
from pathlib import Path

import click
from click import pass_context

from alpa.repository import AlpaRepo


pkg_name = click.argument("name", type=str)


@click.group()
@pass_context
def alpa_repo(ctx) -> None:
    ctx.obj = AlpaRepo(Path(getcwd()))


@alpa_repo.command("create")
@pkg_name
@pass_context
def create(ctx, name: str) -> None:
    """Create new package"""
    ctx.obj.create_package(name)


@alpa_repo.command("delete")
@pkg_name
@pass_context
def delete(ctx, name: str) -> None:
    """Delete existing package"""
    pass


@alpa_repo.command("request-package")
@pkg_name
@pass_context
def request_package(ctx, name: str) -> None:
    """Request new branch for new package in upstream"""
    ctx.obj.request_package(name)
