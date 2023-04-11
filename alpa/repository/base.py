"""
Set of commands that helps with integration of Alpa
repository.
"""
import subprocess
from abc import ABC, abstractmethod
from os import getcwd, environ
from pathlib import Path
from subprocess import call
from tempfile import NamedTemporaryFile
from typing import Optional, Iterable
from urllib.parse import urlparse

from click import UsageError, ClickException
import click
from git import Repo, Remote

from alpa.constants import (
    ALPA_FEAT_BRANCH,
    ALPA_FEAT_BRANCH_PREFIX,
    ORIGIN_NAME,
    UPSTREAM_NAME,
)
from alpa.gh import GithubAPI, GithubRepo
from alpa.messages import (
    CLONED_REPO_IS_NOT_FORK,
    NOT_IN_PREDEFINED_STATE,
    CLONED_REPO_IS_FORK,
    NO_PERMISSION_FOR_ALPA_REPO,
)


class LocalRepo(ABC):
    def __init__(self, repo_path: Path) -> None:
        self.repo_path = repo_path
        # TODO: this will differ in the future with repo_path
        self.repo_root_path = repo_path
        self.local_repo = Repo(str(self.repo_path), search_parent_directories=True)
        self.git_cmd = self.local_repo.git

        if not self._is_repo_in_predefined_state():
            raise ClickException(NOT_IN_PREDEFINED_STATE)

        # do it after predefined state is checked since this depends on it
        # (see comment in the _should_be_fork)
        self.remote_name = UPSTREAM_NAME if self._should_be_fork() else ORIGIN_NAME

        # lazy properties
        self._namespace: Optional[str] = None
        self._repo_name: Optional[str] = None
        self._git_root: Optional[Path] = None

    @abstractmethod
    def get_packages(self, regex: str) -> list[str]:
        pass

    @abstractmethod
    def switch_to_package(self, package: str) -> None:
        pass

    @abstractmethod
    def _ensure_feature_branch(self) -> None:
        pass

    @abstractmethod
    def get_history_of_package(self, package: str) -> str:
        pass

    @property
    @abstractmethod
    def package(self) -> str:
        pass

    @abstractmethod
    def create_packit_config(self, override: bool) -> bool:
        pass

    @property
    def remote_associated_with_current_branch(self) -> str:
        return self.local_repo.active_branch.tracking_branch().remote_name

    @property
    def branch(self) -> str:
        return self.local_repo.active_branch.name

    @staticmethod
    def get_feat_branch_of_package(package: str) -> str:
        return ALPA_FEAT_BRANCH.format(pkgname=package)

    @property
    def feat_branch(self) -> str:
        return ALPA_FEAT_BRANCH.format(pkgname=self.package)

    @staticmethod
    def _get_relevant_remote_refs(remote_refs: Iterable[str]) -> list[str]:
        relevant_refs = []
        for ref in remote_refs:
            parsed_ref = ref.split("/")[-1]
            if not parsed_ref.startswith(ALPA_FEAT_BRANCH_PREFIX):
                relevant_refs.append(parsed_ref)

        return relevant_refs

    def get_remote_branches(self, remote: str) -> list[str]:
        lines = [
            line.strip()
            for line in self.git_cmd.remote("--verbose", "show", remote).split("\n")
        ]
        # TODO: do a better job
        remote_branch_line = ["Remote branch:", "Remote branches:"]
        start = -1
        for line_to_match in remote_branch_line:
            if line_to_match in lines:
                start = lines.index(line_to_match)
                break

        if start == -1:
            return []

        # TODO: do a better job
        possible_start_of_local_stuff = [
            "Local branch configured for 'git pull':",
            "Local branches configured for 'git pull':",
            "Local ref configured for 'git push':",
            "Local refs configured for 'git push':",
        ]
        end = -1
        for line_to_match in possible_start_of_local_stuff:
            if line_to_match in lines:
                end = lines.index(line_to_match)
                break

        if end == -1:
            end = len(lines)

        lines_with_remote_branches = lines[start + 1 : end]
        return [line.split()[0] for line in lines_with_remote_branches]

    def _is_repo_in_predefined_state(self) -> bool:
        remotes_name_set = {remote.name for remote in self.local_repo.remotes}
        return remotes_name_set == {ORIGIN_NAME, UPSTREAM_NAME} or remotes_name_set == {
            ORIGIN_NAME
        }

    def _should_be_fork(self) -> bool:
        remotes_name_set = {remote.name for remote in self.local_repo.remotes}
        # if repo is prepared via alpa-cli, fork should have 2 remotes and non-fork 1
        return len(remotes_name_set) > 1

    @property
    def untracked_files(self) -> list[str]:
        return self.local_repo.untracked_files

    def _get_dirty_files(self, staged: bool) -> list[str]:
        result = []
        status_output = self.git_cmd.status("--porcelain=1").split("\n")
        for line in status_output:
            file = line.split()[-1]
            if line.startswith("MM"):
                result.append(file)
                continue

            if not staged and line.startswith(" M"):
                result.append(file)
                continue

            if staged and line.startswith("M "):
                result.append(file)
                continue

        return result

    @property
    def modified_files(self) -> list[str]:
        return self._get_dirty_files(False)

    @property
    def files_to_be_committed(self) -> list[str]:
        return self._get_dirty_files(True)

    @property
    def namespace(self) -> str:
        if self._namespace is not None:
            return self._namespace

        self._namespace = self.full_reponame().split("/")[0]
        return self._namespace

    @property
    def repo_name(self) -> str:
        if self._repo_name is not None:
            return self._repo_name

        self._repo_name = self.full_reponame().split("/")[1]
        return self._repo_name

    @staticmethod
    def _format_files_to_status(files: list[str], msg: str) -> str:
        if not files:
            return ""

        output = msg + "\n"
        output += "\n".join(files)
        return output + "\n"

    def get_status_output(self) -> str:
        output = self._format_files_to_status(
            self.files_to_be_committed, "Files to commit:"
        )
        output += self._format_files_to_status(self.modified_files, "Modified files:")
        output += self._format_files_to_status(self.untracked_files, "Untracked files:")
        return output

    def branch_exists(self, branch: str) -> bool:
        for ref in self.local_repo.references:
            if ref.name == branch:
                return True

        return False

    def get_history_of_branch(self, branch: str, *params: list[str]) -> str:
        return self.git_cmd.log("--decorate", "--graph", *params, branch)

    @staticmethod
    def _get_message_from_editor() -> str:
        with NamedTemporaryFile(suffix=".alpa.tmp") as temp_file:
            call([environ.get("EDITOR", "vim"), temp_file.name])
            temp_file.seek(0)
            output = temp_file.read()
            if isinstance(output, (bytes, bytearray)):
                return output.decode("utf-8")

            return output

    def commit(self, message: str, pre_commit: bool) -> bool:
        if pre_commit:
            ret = subprocess.run(["pre-commit", "run", "--all-files"])
            if ret.returncode != 0:
                return False

        self._ensure_feature_branch()
        index = self.local_repo.index
        if message:
            index.commit(message)
        else:
            index.commit(self._get_message_from_editor())

        return True

    def add(self, files: list[str]) -> None:
        self._ensure_feature_branch()
        # FIXME: alpa add . acts weird
        self.git_cmd.add(files)

    def pull(self, branch: str) -> None:
        click.echo(self.git_cmd.pull(self.remote_name, branch))

    def push(self, branch: str) -> None:
        # you always want to push to origin, even from a fork
        click.echo(self.git_cmd.push(ORIGIN_NAME, branch))

    def full_reponame(self) -> str:
        for remote in self.local_repo.remotes:
            if remote.name == self.remote_name:
                return remote.url.split(":")[-1].removesuffix(".git")

        return ""

    @property
    def git_root(self) -> Optional[Path]:
        if self._git_root is not None:
            return self._git_root

        self._git_root = Path(self.local_repo.working_tree_dir)
        return self._git_root


class AlpaRepo(LocalRepo):
    def __init__(self, repo_path: Path, gh_api: Optional[GithubAPI] = None) -> None:
        super().__init__(repo_path)

        self.gh_api = gh_api or GithubAPI(self.repo_name)
        self.gh_repo = self.gh_api.get_repo(self.namespace, self.repo_name)

    @abstractmethod
    def create_package(self, package: str) -> None:
        pass

    @abstractmethod
    def request_package(self, package_name: str) -> None:
        pass

    @abstractmethod
    def request_package_delete(self, package: str) -> None:
        pass

    @staticmethod
    def _prepare_cloned_repo(local_repo: Repo, gh_repo: GithubRepo) -> None:
        if not gh_repo.is_fork:
            return

        Remote.create(local_repo, UPSTREAM_NAME, gh_repo.upstream_clone_url)

    @staticmethod
    def _get_repo_name_from_url(repo_url: str) -> str:
        return repo_url.split("/")[-1].removesuffix(".git")

    @staticmethod
    def _check_for_permission_and_fork(
        clone_fork: bool, gh_repo: GithubRepo
    ) -> tuple[bool, str]:
        if clone_fork and not gh_repo.is_fork:
            return False, CLONED_REPO_IS_NOT_FORK

        if not clone_fork and gh_repo.is_fork:
            return False, CLONED_REPO_IS_FORK

        if not gh_repo.is_fork and not gh_repo.has_write_access(gh_repo.api_user):
            return False, NO_PERMISSION_FOR_ALPA_REPO

        return True, ""

    @classmethod
    def clone(cls, url: str, clone_fork: bool) -> None:
        # in case of `@` in url -> remove the `git@` prefix form it
        repo_path = urlparse(url.split("@")[-1]).path
        parsed_repo_path = repo_path.strip("/").strip(".git")
        namespace, repo_name = parsed_repo_path.split("/")
        api = GithubAPI(repo_name)
        gh_repo = api.get_repo(namespace, repo_name)

        check_result, stderr = cls._check_for_permission_and_fork(clone_fork, gh_repo)
        if not check_result:
            raise UsageError(stderr)

        cloned_repo = Repo.clone_from(
            url, f"{getcwd()}/{cls._get_repo_name_from_url(url)}"
        )
        cls._prepare_cloned_repo(cloned_repo, gh_repo)
