from os import getcwd
from pathlib import Path
import click

from click import Choice, pass_context
from alpa.repository import FAPRepo


pkg_name = click.argument("name", type=str)


@click.group()
@pass_context
def alpa(ctx) -> None:
    ctx.obj = FAPRepo(Path(getcwd()))


@alpa.command("show-history")
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

    fap = ctx.obj
    fap.get_history_of_branch(fap.package, *params)


@alpa.command("create")
@pkg_name
@pass_context
def create(ctx, name: str) -> None:
    """Create new package"""
    ctx.obj.create_package(name)


@alpa.command("delete")
@pkg_name
@pass_context
def delete(ctx, name: str) -> None:
    """Delete existing package"""
    pass


@alpa.command("switch")
@pkg_name
@pass_context
def switch(ctx, name: str) -> None:
    """Switch to specified package"""
    ctx.obj.switch_to_package(name)


@alpa.command("request-package")
@pkg_name
@pass_context
def request_package(ctx, name: str) -> None:
    """Request new branch for new package in upstream"""
    ctx.obj.request_package(name)


@alpa.command("commit")
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
    ctx.obj.commit(message)


@alpa.command("push")
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
    fap = ctx.obj
    fap.push(fap.package)

    if pull_request:
        fap.gh_repo.create_pr()


@alpa.command("pull")
@pass_context
def pull(ctx) -> None:
    """Pull last recent changes of package you are on from upstream"""
    ctx.obj.pull(ctx.obj.branch)


@alpa.command("clone")
@click.argument("url", type=str)
def clone(url: str) -> None:
    """Clone and prepare Fedora Alternative Packaging repository"""
    FAPRepo.clone(url)


@alpa.command("list")
@click.option("-p", "--pattern", type=str, default="", help="Optional pattern to match")
@pass_context
def list(ctx, regex: str) -> None:
    """List all packages or packages matching regex"""
    for pkg in ctx.obj.get_packages(regex):
        click.echo(pkg)


@alpa.command("genspec")
@click.option(
    "--lang",
    type=Choice(["python", "java"], case_sensitive=False),
    required=True,
    help="Choose the prohramming language for which the generator is designed",
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


FAPRepo(Path(getcwd()))


if __name__ == "__main__":
    alpa()
