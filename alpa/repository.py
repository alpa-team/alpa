"""
Set of commands that helps with integration of Fedora Alternative Packaging
repository.
"""


from os import getcwd
from pathlib import Path
import re
from typing import List, Optional
from urllib.parse import urlparse

from click import UsageError, ClickException
import click
from git import Repo, Remote
from alpa.constants import (
    FAP_FEAT_BRANCH,
    FAP_FEAT_BRANCH_PREFIX,
    MAIN_BRANCH,
    ORIGIN_NAME,
    UPSTREAM_NAME,
    PackageRequest,
)
from alpa.github import GithubAPI
from alpa.messages import (
    CLONED_REPO_IS_NOT_FORK,
    NO_WRITE_ACCESS_ERR,
)


class FAPRepo:
    def __init__(
        self,
        repo_path: Path,
        gh_api: Optional[GithubAPI] = None,
    ) -> None:
        self.repo_path = repo_path
        self.local_repo = Repo(self.repo_path)
        self.git_cmd = self.local_repo.git

        self.gh_api = gh_api or GithubAPI()

        repo_name = "repo_name"
        namespace = "the_namespace"
        self.gh_repo = self.gh_api.get_repo(namespace, repo_name)

    @property
    def branch(self) -> str:
        return self.local_repo.active_branch.tracking_branch().remote_name

    @property
    def package(self) -> str:
        return self.branch.lstrip(FAP_FEAT_BRANCH_PREFIX)

    def get_packages(self, regex: str) -> List[str]:
        remote_refs = self.local_repo.remote(name=UPSTREAM_NAME).refs
        if regex == "":
            return list(remote_refs)

        pattern = re.compile(regex)
        return [pkg for pkg in remote_refs if pattern.match(pkg)]

    def _is_repo_in_predefined_state(self) -> bool:
        remotes_name_set = {remote.name for remote in self.local_repo.remotes}
        return remotes_name_set == {ORIGIN_NAME, UPSTREAM_NAME}

    def _prepare_cloned_repo(self) -> None:
        Remote.create(self.local_repo, UPSTREAM_NAME, self.gh_repo.upstream_url)

    @staticmethod
    def clone(url: str) -> None:
        # in case of `@` in url -> remove the `git@` prefix form it
        repo_path = urlparse(url.split("@")[-1]).path
        parsed_repo_path = repo_path.strip("/").strip(".git")
        namespace, repo_name = parsed_repo_path.split("/")
        api = GithubAPI()
        gh_repo = api.get_repo(namespace, repo_name)
        if not gh_repo.is_fork():
            raise UsageError(CLONED_REPO_IS_NOT_FORK)

        cloned_repo = Repo.clone_from(url, getcwd())
        FAPRepo(cloned_repo.working_dir, api)._prepare_cloned_repo()

    def pull(self, branch: str) -> None:
        self.git_cmd.pull(ORIGIN_NAME, branch)

    def push(self, branch: str) -> None:
        self.git_cmd.push(ORIGIN_NAME, f"{self.branch}:{branch}")

    def commit(self, message: str) -> None:
        if self.branch == self.package:
            click.echo("Switching to feature branch")
            self.git_cmd.switch("-c", FAP_FEAT_BRANCH.format(pkgname=self.package))

        index = self.local_repo.index
        index.add("*")
        if message:
            index.commit(message)
        else:
            index.commit()

    def create_package(self, package: str) -> None:
        upstream = self.gh_repo.get_upstream()
        if upstream and not upstream.has_write_access(self.gh_api.gh_user):
            raise ClickException(NO_WRITE_ACCESS_ERR)

        self.git_cmd.switch(MAIN_BRANCH)
        self.git_cmd.switch("-c", package)
        self.push(package)

    def switch_to_package(self, package: str) -> None:
        self.git_cmd.switch(package)

    def request_package(self, package_name: str) -> None:
        upstream = self.gh_repo.get_upstream()
        if upstream is None:
            upstream = self.gh_repo

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

    def get_history_of_branch(self, branch: str, *params: List[str]) -> None:
        return self.git_cmd.log("--all", "--decorate", "--graph", *params, branch)
