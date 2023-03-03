import click

from click import Choice

from alpa.cli.alpa_repo import alpa_repo
from alpa.cli.local_repo import local_repo
from alpa.repository import AlpaRepo


@click.group()
def base() -> None:
    pass


@base.command("genspec")
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


@base.command("clone")
@click.argument("url", type=str)
def clone(url: str) -> None:
    """Clone and prepare Alpa repository"""
    AlpaRepo.clone(url)


entry_point = click.CommandCollection(sources=[base, alpa_repo, local_repo])


if __name__ == "__main__":
    entry_point()
