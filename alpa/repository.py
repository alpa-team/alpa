"""
Set of commands that helps with integration of Alpa
repository.
"""
from os import getcwd, environ
from pathlib import Path
import re
from subprocess import call
from tempfile import NamedTemporaryFile
from typing import List, Optional
from urllib.parse import urlparse

from click import UsageError, ClickException
import click
from git import Repo, Remote
from alpa.constants import (
    ALPA_FEAT_BRANCH,
    ALPA_FEAT_BRANCH_PREFIX,
    MAIN_BRANCH,
    ORIGIN_NAME,
    UPSTREAM_NAME,
    PackageRequest,
)
from alpa.gh import GithubAPI, GithubRepo
from alpa.messages import (
    CLONED_REPO_IS_NOT_FORK,
    NO_WRITE_ACCESS_ERR,
    NOT_IN_PREDEFINED_STATE,
)


class LocalRepo:
    def __init__(self, repo_path: Path) -> None:
        self.repo_path = repo_path
        self.local_repo = Repo(str(self.repo_path))
        self.git_cmd = self.local_repo.git

        if not self._is_repo_in_predefined_state():
            raise ClickException(NOT_IN_PREDEFINED_STATE)

    @property
    def branch(self) -> str:
        return self.local_repo.active_branch.tracking_branch().remote_name

    @property
    def package(self) -> str:
        return self.branch.lstrip(ALPA_FEAT_BRANCH_PREFIX)

    def get_packages(self, regex: str) -> List[str]:
        remote_refs = self.local_repo.remote(name=UPSTREAM_NAME).refs
        if regex == "":
            return [pkg.name for pkg in remote_refs]

        pattern = re.compile(regex)
        return [pkg.name for pkg in remote_refs if pattern.match(pkg)]

    def _is_repo_in_predefined_state(self) -> bool:
        remotes_name_set = {remote.name for remote in self.local_repo.remotes}
        return remotes_name_set == {ORIGIN_NAME, UPSTREAM_NAME}

    def switch_to_package(self, package: str) -> None:
        self.git_cmd.switch(package)

    def get_history_of_branch(self, branch: str, *params: List[str]) -> None:
        return self.git_cmd.log("--all", "--decorate", "--graph", *params, branch)

    @staticmethod
    def _get_message_from_editor() -> str:
        with NamedTemporaryFile(suffix=".alpa.tmp") as temp_file:
            call([environ.get("EDITOR", "vim"), temp_file.name])
            temp_file.seek(0)
            output = temp_file.read()
            if isinstance(output, (bytes, bytearray)):
                return output.decode("utf-8")

            return output

    def commit(self, message: str) -> None:
        if self.branch == self.package:
            click.echo("Switching to feature branch")
            self.git_cmd.switch("-c", ALPA_FEAT_BRANCH.format(pkgname=self.package))

        index = self.local_repo.index
        index.add("*")
        if message:
            index.commit(message)
        else:
            index.commit(self._get_message_from_editor())

    def pull(self, branch: str) -> None:
        self.git_cmd.pull(ORIGIN_NAME, branch)

    def push(self, branch: str) -> None:
        self.git_cmd.push(ORIGIN_NAME, f"{self.branch}:{branch}")

    def _get_full_reponame(self) -> str:
        for remote in self.local_repo.remotes:
            if remote.name == ORIGIN_NAME:
                return remote.url.split(":")[-1].rstrip(".git")

        return ""


class AlpaRepo(LocalRepo):
    def __init__(self, repo_path: Path, gh_api: Optional[GithubAPI] = None) -> None:
        super().__init__(repo_path)

        self.gh_api = gh_api or GithubAPI()
        namespace, repo_name = self._get_full_reponame().split("/")
        self.gh_repo = self.gh_api.get_repo(namespace, repo_name)

    def create_package(self, package: str) -> None:
        upstream = self.gh_repo.get_upstream()
        if upstream and not upstream.has_write_access(self.gh_api.gh_user):
            raise ClickException(NO_WRITE_ACCESS_ERR)

        self.git_cmd.switch(MAIN_BRANCH)
        self.git_cmd.switch("-c", package)
        self.push(package)

    def request_package(self, package_name: str) -> None:
        upstream = self.gh_repo.get_root_repo()
        upstream_namespace = upstream.namespace
        issue_repo = self.gh_api.get_repo(upstream_namespace, self.gh_repo.repo_name)
        issue = issue_repo.create_issue(
            PackageRequest.TITLE.value.format(package_name=package_name),
            PackageRequest.BODY.value.format(
                user=self.gh_api.gh_user,
                package_name=package_name,
                repo_name=self.gh_repo.repo_name,
            ),
        )
        issue.add_to_labels(PackageRequest.LABEL)

    def delete_package(self) -> None:
        pass

    @staticmethod
    def _prepare_cloned_repo(local_repo: Repo, gh_repo: GithubRepo) -> None:
        # tady je potreba to neudelat v self
        Remote.create(local_repo, UPSTREAM_NAME, gh_repo.upstream_url)

    @staticmethod
    def _get_repo_name_from_url(repo_url: str) -> str:
        return repo_url.split("/")[-1].rstrip(".git")

    @classmethod
    def clone(cls, url: str) -> None:
        # in case of `@` in url -> remove the `git@` prefix form it
        repo_path = urlparse(url.split("@")[-1]).path
        parsed_repo_path = repo_path.strip("/").strip(".git")
        namespace, repo_name = parsed_repo_path.split("/")
        api = GithubAPI()
        gh_repo = api.get_repo(namespace, repo_name)
        if not gh_repo.is_fork():
            raise UsageError(CLONED_REPO_IS_NOT_FORK)

        cloned_repo = Repo.clone_from(url, getcwd() + cls._get_repo_name_from_url(url))
        cls._prepare_cloned_repo(cloned_repo, gh_repo)
