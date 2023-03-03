from os import getcwd
from pathlib import Path

import click
from click import pass_context, ClickException

from alpa.repository import LocalRepo


pkg_name = click.argument("name", type=str)


@click.group()
@pass_context
def local_repo(ctx) -> None:
    ctx.obj = LocalRepo(Path(getcwd()))


@local_repo.command("show-history")
@click.option(
    "-o",
    "--oneline",
    is_flag=True,
    show_default=True,
    default=False,
    help="Each commit is displayed as one line",
)
@pass_context
def show_history(ctx, oneline: bool) -> None:
    """Show git history of current package"""
    params = []
    if oneline:
        params.append("--oneline")

    local = ctx.obj
    local.get_history_of_branch(local.package, *params)


@local_repo.command("switch")
@pkg_name
@pass_context
def switch(ctx, name: str) -> None:
    """Switch to specified package"""
    ctx.obj.switch_to_package(name)


@local_repo.command("commit")
@click.option(
    "-m",
    "--message",
    type=str,
    default="",
    help="Your commit message not longer than 80 characters.",
)
@pass_context
def commit(ctx, message: str) -> None:
    """Commit your changes in your package's repository"""
    if len(message) > 80:
        raise ClickException("Message longer than 80 characters")

    ctx.obj.commit(message)


@local_repo.command("push")
@click.option(
    "-p",
    "--pull-request",
    is_flag=True,
    show_default=True,
    default=False,
    help="This will create pull request on GitHub for you.",
)
@pass_context
def push(ctx, pull_request: bool) -> None:
    """Pushes your commited changes to the upstream so you can make PR"""
    alpa = ctx.obj
    alpa.push(alpa.package)

    if pull_request:
        alpa.gh_repo.create_pr()


@local_repo.command("pull")
@pass_context
def pull(ctx) -> None:
    """Pull last recent changes of package you are on from upstream"""
    ctx.obj.pull(ctx.obj.branch)


@local_repo.command("list")
@click.option("-p", "--pattern", type=str, default="", help="Optional pattern to match")
@pass_context
def list(ctx, regex: str) -> None:
    """List all packages or packages matching regex"""
    for pkg in ctx.obj.get_packages(regex):
        click.echo(pkg)
