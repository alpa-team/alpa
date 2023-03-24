import click
import requests

from alpa_conf.metadata import Metadata

from alpa.cli.alpa_repo import create, delete, request_package
from alpa.cli.local_repo import (
    show_history,
    switch,
    commit,
    pull,
    push,
    list,
    genspec,
    add,
)
from alpa.repository import AlpaRepo


@click.group()
def entry_point() -> None:
    pass


# commands that don't require git repo at all


@entry_point.command("clone")
@click.argument("url", type=str)
def clone(url: str) -> None:
    """Clone and prepare Alpa repository"""
    AlpaRepo.clone(url)


@entry_point.command("get-pkg-archive")
def get_pkg_archive() -> None:
    """Gets archive from package config"""
    metadata = Metadata()
    resp = requests.get(metadata.upstream_url, allow_redirects=True)
    if not resp.ok:
        raise ConnectionError(
            f"Couldn't download source from {metadata.upstream_url}. "
            f"Reason: {resp.reason}"
        )

    with open(
        f"{metadata.package_name}-{metadata.upstream_version}.tar.gz", "wb"
    ) as archive:
        archive.write(resp.content)


entry_point.add_command(create)
entry_point.add_command(delete)
entry_point.add_command(request_package)

entry_point.add_command(show_history)
entry_point.add_command(switch)
entry_point.add_command(commit)
entry_point.add_command(pull)
entry_point.add_command(push)
entry_point.add_command(list)
entry_point.add_command(genspec)
entry_point.add_command(add)


if __name__ == "__main__":
    entry_point()
