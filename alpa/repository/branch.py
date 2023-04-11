"""
Set of commands that helps with integration of Alpa
repository.
"""

from pathlib import Path
import re
from typing import Optional, Type

from click import ClickException
import click
from git import GitCommandError

from alpa.config import PackitConfig
from alpa.constants import (
    ALPA_FEAT_BRANCH_PREFIX,
    MAIN_BRANCH,
    PackageRequest,
    DeleteRequest,
    REQUEST_LABEL,
)
from alpa.gh import GithubAPI
from alpa.messages import NO_WRITE_ACCESS_ERR
from alpa.repository.base import LocalRepo, AlpaRepo


class LocalRepoBranch(LocalRepo):
    def __init__(self, repo_path: Path) -> None:
        super().__init__(repo_path)

    @property
    def package(self) -> str:
        return self.branch.removeprefix(ALPA_FEAT_BRANCH_PREFIX)

    def get_history_of_package(self, package: str) -> str:
        raise NotImplementedError("Please implement me!")

    def get_packages(self, regex: str) -> list[str]:
        # self.local_repo.remote(name=self.remote_name).refs don't work on every case
        refs_without_main = filter(
            lambda ref: ref != "main", self.get_remote_branches(self.remote_name)
        )
        relevant_refs = self._get_relevant_remote_refs(refs_without_main)

        if regex == "":
            return list(relevant_refs)

        pattern = re.compile(regex)
        return [ref for ref in relevant_refs if pattern.match(ref)]

    def switch_to_package(self, package: str) -> None:
        if self.local_repo.is_dirty():
            click.echo(
                "Repo is dirty, please commit your changes before switching to"
                f" another package.\n {self.get_status_output()}"
            )
            return None

        feat_branch = self.get_feat_branch_of_package(package)
        branch_to_switch = feat_branch if self.branch_exists(feat_branch) else package
        try:
            click.echo(
                self.git_cmd.switch(branch_to_switch).replace("branch", "package")
            )
        except GitCommandError:
            # switching to the package for the first time
            click.echo(f"Switching to the package {package} for the first time")
            click.echo(self.git_cmd.fetch(self.remote_name, branch_to_switch))
            click.echo(
                self.git_cmd.switch(branch_to_switch).replace("branch", "package")
            )

    def _ensure_feature_branch(self) -> None:
        if self.branch != self.package:
            return None

        click.echo("Switching to feature branch")
        self.git_cmd.switch("-c", self.feat_branch)

    def create_packit_config(self, override: bool) -> bool:
        packit_conf = PackitConfig(self.package)
        if packit_conf.packit_config_file_exists() and not override:
            return False

        packit_conf.create_packit_config()
        return True


class AlpaRepoBranch(AlpaRepo, LocalRepoBranch):
    def __init__(self, repo_path: Path, gh_api: Optional[GithubAPI] = None) -> None:
        super().__init__(repo_path, gh_api)

        self.gh_api = gh_api or GithubAPI(self.repo_name)
        self.gh_repo = self.gh_api.get_repo(self.namespace, self.repo_name)

    def create_package(self, package: str) -> None:
        upstream = self.gh_repo.get_upstream()
        if upstream and not upstream.has_write_access(self.gh_api.gh_user):
            raise ClickException(NO_WRITE_ACCESS_ERR)

        self.git_cmd.switch(MAIN_BRANCH)
        self.git_cmd.switch("-c", package)
        self.git_cmd.push(self.remote_name, package)
        click.echo(f"Package {package} created")

    def _request_package_action(
        self, action: Type[PackageRequest | DeleteRequest], pkg: str
    ) -> None:
        ensured_upstream = self.gh_repo.get_root_repo()
        upstream_namespace = ensured_upstream.namespace
        issue_repo = self.gh_api.get_repo(upstream_namespace, self.gh_repo.repo_name)
        issue = issue_repo.create_issue(
            action.TITLE.value.format(package_name=pkg),
            action.BODY.value.format(
                user=self.gh_api.gh_user,
                package_name=pkg,
            ),
        )
        issue.add_to_labels(REQUEST_LABEL)

    def request_package(self, package_name: str) -> None:
        self._request_package_action(PackageRequest, package_name)

    def request_package_delete(self, package: str) -> None:
        self._request_package_action(DeleteRequest, package)
