"""
These commands need to create LocalRepo -> no GH token required
"""


from os import getcwd
from pathlib import Path

import click
from click import ClickException, Choice

from alpa.repository import LocalRepo


pkg_name = click.argument("name", type=str)


@click.command("show-history")
@click.option(
    "-o",
    "--oneline",
    is_flag=True,
    show_default=True,
    default=False,
    help="Each commit is displayed as one line",
)
def show_history(oneline: bool) -> None:
    """Show git history of current package"""
    params = []
    if oneline:
        params.append("--oneline")

    local_repo = LocalRepo(Path(getcwd()))
    local_repo.get_history_of_branch(local_repo.package, *params)


@click.command("switch")
@pkg_name
def switch(name: str) -> None:
    """Switch to specified package"""
    LocalRepo(Path(getcwd())).switch_to_package(name)


@click.command("commit")
@click.option(
    "-m",
    "--message",
    type=str,
    default="",
    help="Your commit message not longer than 80 characters.",
)
def commit(message: str) -> None:
    """Commit your changes in your package's repository"""
    if len(message) > 80:
        raise ClickException("Message longer than 80 characters")

    LocalRepo(Path(getcwd())).commit(message)


@click.command("push")
@click.option(
    "-p",
    "--pull-request",
    is_flag=True,
    show_default=True,
    default=False,
    help="This will create pull request on GitHub for you.",
)
def push(pull_request: bool) -> None:
    """Pushes your commited changes to the upstream so you can make PR"""
    local_repo = LocalRepo(Path(getcwd()))
    local_repo.push(local_repo.package)

    if pull_request:
        local_repo.gh_repo.create_pr()


@click.command("pull")
def pull() -> None:
    """Pull last recent changes of package you are on from upstream"""
    local_repo = LocalRepo(Path(getcwd()))
    local_repo.pull(local_repo.branch)


@click.command("list")
@click.option("-p", "--pattern", type=str, default="", help="Optional pattern to match")
def list(pattern: str) -> None:
    """List all packages or packages matching regex"""
    for pkg in LocalRepo(Path(getcwd())).get_packages(pattern):
        click.echo(pkg)


@click.command("genspec")
@click.option(
    "--lang",
    type=Choice(["python", "java"], case_sensitive=False),
    required=True,
    help="Choose the programming language for which the generator is designed",
)
@click.option(
    "-t",
    "--test",
    default=False,
    help=(
        "Send package with generated spec file to "
        "packit to test whether build will succeed."
    ),
)
def genspec(lang: str, test: bool) -> None:
    """This command uses some existing spec file generators for you"""
    pass
