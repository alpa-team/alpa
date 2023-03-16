"""
These commands need to create LocalRepo -> no GH token required
"""


from os import getcwd
from pathlib import Path
from typing import List

import click
from click import ClickException, Choice

from alpa.repository import LocalRepo, AlpaRepo

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
    click.echo(local_repo.get_history_of_branch(local_repo.package, params))


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


@click.command("add")
@click.argument("files", type=str, nargs=-1, required=True)
def add(files: List[str]) -> None:
    """Add files to git history. Basically calls `git add <input>`"""
    LocalRepo(Path(getcwd())).add(files)


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
    repo_path = Path(getcwd())
    local_repo = LocalRepo(repo_path)
    local_repo.push(local_repo.branch)

    if not pull_request:
        return

    alpa = AlpaRepo(repo_path)
    pr = alpa.gh_repo.create_pr(
        title=f"[alpa-cli] Create update of package {local_repo.package}",
        # TODO this should provide at least some short descriptive message
        body="",
        source_branch=f"{alpa.gh_api.gh_user}:{local_repo.feat_branch}",
        target_branch=local_repo.package,
    )
    click.echo(f"PR#{pr.id} created. URL: {pr.url}")


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
    raise NotImplementedError("Not implemented yet (1.0 goal)")
