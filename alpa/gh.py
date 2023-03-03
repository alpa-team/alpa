"""
Integration with GitHub API.
"""


from os import getenv
from typing import Optional
from click import UsageError
from github import Github, Issue, PullRequest

from alpa.constants import GH_API_TOKEN_NAME, GH_WRITE_ACCESS
from alpa.messages import NO_GH_API_KEY_FOUND


class GithubRepo:
    def __init__(self, api: Github, namespace: str, repo_name: str) -> None:
        self.namespace = namespace
        self.repo_name = repo_name

        self._api = api
        self._repo = api.get_repo(f"{namespace}/{repo_name}")

    @property
    def url(self) -> str:
        return self._repo.url

    @property
    def upstream_url(self) -> Optional[str]:
        upstream = self.get_upstream()
        if upstream is None:
            return None

        return upstream.url

    def is_fork(self) -> bool:
        return self._repo.fork

    def has_write_access(self, user: str) -> bool:
        for collaborator in self._repo.get_collaborators():
            if collaborator != user:
                continue

            return (
                self._repo.get_collaborator_permission(collaborator) in GH_WRITE_ACCESS
            )

        return False

    def get_upstream(self) -> Optional["GithubRepo"]:
        if not self.is_fork():
            return None

        namespace, repo_name = self._repo.source.full_name.split("/")
        return GithubRepo(self._api, namespace, repo_name)

    def get_root_repo(self) -> "GithubRepo":
        root_repo = self.get_upstream()
        if root_repo is None:
            root_repo = self

        return root_repo

    def create_issue(self, title: str, body: str) -> Issue:
        return self.get_root_repo()._repo.create_issue(title, body)

    def create_pr(
        self, title: str, body: str, source_branch: str, target_branch: str = "main"
    ) -> PullRequest:
        return self.get_root_repo()._repo.create_pull(
            title, body, base=target_branch, head=source_branch
        )


class GithubAPI:
    def __init__(self) -> None:
        self._gh_api = Github(self._get_access_token())

    @property
    def gh_user(self) -> str:
        return self._gh_api.get_user().login

    @staticmethod
    def _get_access_token() -> str:
        access_token = getenv(GH_API_TOKEN_NAME)
        if access_token is None:
            raise UsageError(NO_GH_API_KEY_FOUND.format(token=GH_API_TOKEN_NAME))

        return access_token

    def get_repo(self, namespace: str, repo_name: str) -> GithubRepo:
        return GithubRepo(self._gh_api, namespace, repo_name)
