from pathlib import Path
from unittest.mock import patch, PropertyMock

import pytest

from alpa.constants import ALPA_FEAT_BRANCH_PREFIX
from alpa.repository.base import LocalRepo
from alpa.repository.branch import LocalRepoBranch
from test.fake_alpa_repo import FakeAlpaBranchRepo, FakeAlpaRepo


class Test:
    def test_get_feat_branch_of_package(self):
        assert LocalRepo.get_feat_branch_of_package("pkg") == "__feat_pkg"

    @pytest.mark.parametrize(
        "remote_refs, result",
        [
            pytest.param(["raz", "dva", "tri"], ["raz", "dva", "tri"]),
            pytest.param(["dva", "__feat_dva", "tri"], ["dva", "tri"]),
            pytest.param([], []),
            pytest.param(["__feat_branch"], []),
        ],
    )
    def test_get_relevant_remote_refs(self, remote_refs, result):
        assert LocalRepo._get_relevant_remote_refs(remote_refs) == result

    def test_parse_reponame_from_url(self):
        assert (
            LocalRepo._parse_reponame_from_url("https://example.org/namespace/repo.git")
            == "namespace/repo"
        )
        assert (
            LocalRepo._parse_reponame_from_url("git@example.org:namespace/repo.git")
            == "namespace/repo"
        )


class TestBaseRepo(FakeAlpaRepo):
    def test_get_branch(self):
        branch = "test-branch"
        self.git_cmd(["switch", "-c", branch])
        assert self.local_repo.branch == branch

    @patch.object(LocalRepo, "package", new_callable=PropertyMock)
    def test_get_feat_branch(self, mock_package):
        branch = "test-branch"
        mock_package.return_value = branch

        self.git_cmd(["switch", "-c", branch])
        assert self.local_repo.feat_branch == "__feat_test-branch"

    def test_get_remote_branches(self):
        result = ["main"]
        for branch in ["branch1", "branch2", "branch3"]:
            result.append(branch)
            self.git_cmd(["switch", "-c", branch])
            with open(f"{self.local_git_root}/file", "w") as f:
                f.write("some change")

            self.git_cmd(["add", "file"])
            self.git_cmd(["commit", "-m", "commit some change"])
            self.git_cmd(["push", "origin", branch])
            assert sorted(self.local_repo.get_remote_branches("origin")) == sorted(
                result
            )

    def test_remotes(self):
        assert self.local_repo.remotes == {"origin"}

        self.git_cmd(["remote", "add", "something", "fake/remote.git"])
        assert self.local_repo.remotes == {"origin", "something"}

    def test_untracked_files(self):
        with open(f"{self.local_git_root}/file1", "w") as f:
            f.write("file1")

        with open(f"{self.local_git_root}/file2", "w") as f:
            f.write("file2")

        assert self.local_repo.untracked_files == ["file1", "file2"]

    def test_is_dirty(self):
        assert not self.local_repo.is_dirty()

        with open(f"{self.local_git_root}/file", "w") as f:
            f.write("file")

        assert self.local_repo.is_dirty()

        self.git_cmd(["add", "file"])
        assert self.local_repo.is_dirty()

        self.git_cmd(["commit", "-m", "commit file"])
        assert not self.local_repo.is_dirty()

    def test_namespace(self):
        self.git_cmd(
            ["remote", "set-url", "origin", "https://example.org/namespace/repo.git"]
        )
        assert self.local_repo.namespace == "namespace"

        self.git_cmd(
            ["remote", "set-url", "origin", "git@example.org:namespace/repo.git"]
        )
        assert self.local_repo.namespace == "namespace"

    def test_repo_name(self):
        self.git_cmd(
            ["remote", "set-url", "origin", "https://example.org/namespace/repo.git"]
        )
        assert self.local_repo.repo_name == "repo"

        self.git_cmd(
            ["remote", "set-url", "origin", "git@example.org:namespace/repo.git"]
        )
        assert self.local_repo.repo_name == "repo"

    def test_branch_exists(self):
        assert not self.local_repo.branch_exists("new-branch")

        self.git_cmd(["switch", "-c", "new-branch"])
        assert self.local_repo.branch_exists("new-branch")


class TestBranchRepo(FakeAlpaBranchRepo):
    def test_package(self):
        pkg = self.packages[0]
        self.git_cmd(["switch", pkg])
        self.local_repo._ensure_feature_branch()
        assert self.local_repo.package == pkg

    def test_get_packages(self):
        assert set(self.packages) == set(
            LocalRepoBranch(Path(self.local_git_root)).get_packages()
        )

    def test_switch_to_package(self):
        pkg = self.packages[0]
        pkg_to_switch = self.packages[1]
        self.git_cmd(["switch", pkg])
        self.local_repo.switch_to_package(pkg_to_switch)
        assert self.local_repo.package == self.local_repo.branch == pkg_to_switch

    def test_switch_to_non_existing_package(self):
        pkg = self.packages[0]
        self.git_cmd(["switch", pkg])
        self.local_repo.switch_to_package("non-existing-package")
        assert self.local_repo.package == pkg

    def test_switch_to_feat_branch(self):
        pkg = self.packages[0]
        pkg_to_switch = self.packages[1]
        self.git_cmd(["switch", pkg_to_switch])
        self.local_repo._ensure_feature_branch()
        self.git_cmd(["push", "origin", self.local_repo.feat_branch])
        self.git_cmd(["switch", pkg])

        self.local_repo.switch_to_package(pkg_to_switch)
        assert (
            self.local_repo.package == pkg_to_switch
            and self.local_repo.branch.startswith(ALPA_FEAT_BRANCH_PREFIX)
        )

    def test_switch_and_delete_feature_branch(self):
        pkg = self.packages[0]
        pkg_to_switch = self.packages[1]
        self.git_cmd(["switch", pkg_to_switch])
        # no push to remote repo - no feature branch in it -> probably merged
        self.local_repo._ensure_feature_branch()
        self.git_cmd(["switch", pkg])

        self.local_repo.switch_to_package(pkg_to_switch)
        assert self.local_repo.package == self.local_repo.branch == pkg_to_switch

    def test_ensure_feature_branch(self):
        self.local_repo._ensure_feature_branch()
        assert self.local_repo.branch.startswith(ALPA_FEAT_BRANCH_PREFIX)

    def test_rebase_needed(self):
        pkg = self.packages[0]
        self.git_cmd(["switch", pkg])
        assert not self.local_repo._rebase_needed()

        with open(f"{self.local_git_root}/file.txt", "w") as f:
            f.write("something")

        self.git_cmd(["add", "file.txt"])
        self.git_cmd(["commit", "-m", "adding new file"])
        self.git_cmd(["push", "origin", pkg])
        self.git_cmd(["pull", "origin", pkg])
        assert not self.local_repo._rebase_needed()

        self.git_cmd(["switch", "main"], self.other_local_git_root)
        with open(f"{self.other_local_git_root}/.alpa.yaml", "a") as f:
            f.write("adding new line\n")

        self.git_cmd(["add", ".alpa.yaml"], self.other_local_git_root)
        self.git_cmd(["commit", "-m", "new change to main"], self.other_local_git_root)
        self.git_cmd(["push", "origin", "main"], self.other_local_git_root)

        self.git_cmd(["switch", pkg])
        assert self.local_repo._rebase_needed()
