"""
These commands need to create LocalRepo -> no GH token required
"""


from os import getcwd
from pathlib import Path

import click
from click import ClickException, Choice
from specfile import Specfile

from alpa.config import MetadataConfig, PackitConfig
from alpa.repository.branch import LocalRepoBranch, AlpaRepoBranch
from alpa.upstream_integration import UpstreamIntegration

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

    local_repo = LocalRepoBranch(Path(getcwd()))
    click.echo(local_repo.get_history_of_branch(local_repo.branch, params))


@click.command("switch")
@pkg_name
def switch(name: str) -> None:
    """Switch to specified package"""
    LocalRepoBranch(Path(getcwd())).switch_to_package(name)


@click.command("commit")
@click.option(
    "-m",
    "--message",
    type=str,
    default="",
    help="Your commit message not longer than 80 characters.",
)
@click.option("-n", "--no-verify", is_flag=True, help="Do not run pre-commit")
def commit(message: str, no_verify: bool) -> None:
    """Commit your changes in your package's repository"""
    if len(message) > 80:
        raise ClickException("Message longer than 80 characters")

    LocalRepoBranch(Path(getcwd())).commit(message, not no_verify)


@click.command("add")
@click.argument("files", type=str, nargs=-1, required=True)
def add(files: list[str]) -> None:
    """Add files to git history. Basically calls `git add <input>`"""
    LocalRepoBranch(Path(getcwd())).add(files)


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
    """Pushes your commited changes to the Alpa repo so you can make PR"""
    repo_path = Path(getcwd())
    local_repo = LocalRepoBranch(repo_path)

    packit_conf = PackitConfig(local_repo.package)
    if not packit_conf.packit_config_file_exists():
        packit_conf.create_packit_config()
        local_repo.git_cmd.add(".packit.yaml")
        local_repo.git_cmd.commit(
            '-m "alpa: automatically add .packit.yaml config to the package"'
        )

    local_repo.push(local_repo.branch)

    if not pull_request:
        local_repo.git_cmd.branch("-d", local_repo.feat_branch)
        return

    alpa = AlpaRepoBranch(repo_path)
    pr = alpa.gh_repo.create_pr(
        title=f"[alpa-cli] Create update of package {local_repo.package}",
        body=(
            "This PR was created automatically via alpa-cli for "
            f"user {alpa.gh_api.gh_user}"
        ),
        source_branch=f"{local_repo.feat_branch}",
        target_branch=local_repo.package,
    )
    click.echo(f"PR#{pr.number} created. URL: {pr.html_url}")

    # go from feat branch to package branch
    local_repo.git_cmd.switch(local_repo.package)
    local_repo.git_cmd.branch("-D", local_repo.feat_branch)


@click.command("pull")
def pull() -> None:
    """Pull last recent changes of package you are on from Alpa repo"""
    local_repo = LocalRepoBranch(Path(getcwd()))
    local_repo.pull(local_repo.branch)


@click.command("list")
@click.option("-p", "--pattern", type=str, default="", help="Optional pattern to match")
def list_(pattern: str) -> None:
    """List all packages or packages matching regex"""
    for pkg in LocalRepoBranch(Path(getcwd())).get_packages(pattern):
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


@click.command("create-packit-config")
@click.option(
    "--override",
    is_flag=True,
    show_default=True,
    default=False,
    help="Override packit config file",
)
def create_packit_config(override: bool) -> None:
    """Creates packit config based on metadata.yaml file in package"""
    if not LocalRepoBranch(Path(getcwd())).create_packit_config(override):
        raise ClickException(
            "Packit file already exists. To override it use --override flag."
        )


def _get_chroots_to_build(meta: MetadataConfig, distros: list[str]) -> list[str]:
    chroots = []
    for arch in meta.arch:
        for distro in distros:
            chroots.append(f"{distro}-{arch}")
    return chroots


@click.command("mockbuild")
@click.option(
    "--chroot",
    type=str,
    default="",
    help="Override chroots specified in metadata.yaml by one specific chroot",
)
def mockbuild(chroot: str) -> None:
    """
    Uses mock tool to build package. WARNING: works only on rpm-based systems.

    Builds for all chroots specified in metadata.yaml. Can be overriden by --chroot
     option which does build against one specified chroot.
    """
    meta = MetadataConfig.get_config()
    distros = [chroot] if chroot else list(meta.targets)
    chroots = _get_chroots_to_build(meta, distros)
    UpstreamIntegration(Path(getcwd())).mockbuild(chroots)


@click.command("get-pkg-archive")
def get_pkg_archive() -> None:
    """Gets archive from package config"""
    specfile_path = None
    cwd = Path(getcwd())
    for file in cwd.iterdir():
        if str(file).endswith(".spec"):
            specfile_path = file

    if specfile_path is None:
        raise ClickException(f"No specfile found in {cwd}")

    specfile = Specfile(specfile_path)
    with specfile.sources() as sources:
        source0 = min(sources, key=lambda src: src.number)

    UpstreamIntegration.download_upstream_source(
        source0.expanded_location,
        f"{specfile.expanded_name}-{specfile.expanded_version}",
    )
