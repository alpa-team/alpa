"""
Fake local git Alpa repository
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from alpa.repository.base import LocalRepo
from alpa.repository.branch import LocalRepoBranch
from test.constants import METADATA_CONFIG_MANDATORY_ONLY_KEYS

ALPA_CONFIG_BASE = """
---
copr_owner: alpa-owner
copr_repo: alpa-repo
"""

FAKE_SPEC_FILE = """
Name:           test-package
Version:        0.1.0
Release:        1%{?dist}
Summary:        Fake test package

License:        GPLv3
URL:            https://example.com/%{name}
Source0:        %{url}/%{version}.tar.gz


%description
%{summary}


%changelog
* Fri May 12 2023 user@not-google.com
- initial release
"""


class FakeAlpaRepo:
    # ABC stores all abstract methods to `__abstractmethods__`. By setting it to its
    # default empty value, you can make it think like every abstract method was
    # implemented
    @patch("alpa.repository.base.LocalRepo.__abstractmethods__", frozenset())
    def setup_method(self, method):
        self._bare_repo = tempfile.TemporaryDirectory()
        self._local_repo = tempfile.TemporaryDirectory()
        self._other_local_repo = tempfile.TemporaryDirectory()

        self.git_cmd(["--bare", "init"], self._bare_repo.name)
        self._config_git_repo(self._bare_repo.name)
        self.git_cmd(["branch", "-m", "main"], self._bare_repo.name)

        self.local_git_root = self._local_repo.name
        self.git_cmd(["clone", self._bare_repo.name, self.local_git_root])
        self._config_git_repo(self.local_git_root)
        self.git_cmd(["commit", "-m", "Initial commit", "--allow-empty"])
        self.git_cmd(["push"])

        with open(f"{self.local_git_root}/.alpa.yaml", "w") as f:
            f.write(ALPA_CONFIG_BASE)

        self.git_cmd(["add", ".alpa.yaml"])
        self.git_cmd(["commit", "-m", "Add base file for alpa repo config"])
        self.git_cmd(["push"])

        self.other_local_git_root = self._other_local_repo.name
        self.git_cmd(["clone", self._bare_repo.name, self.other_local_git_root])
        self._config_git_repo(self.other_local_git_root)

        self.local_repo = LocalRepo(Path(self.local_git_root))

    def teardown_method(self, method):
        self._bare_repo.cleanup()
        self._local_repo.cleanup()
        self._other_local_repo.cleanup()

    def _config_git_repo(self, repo):
        self.git_cmd(["config", "--local", "user.email", "test-user@example.com"], repo)
        self.git_cmd(["config", "--local", "user.name", "Suspicious Guy"], repo)

    def git_cmd(self, cmd, context=None):
        if context is None and hasattr(self, "local_git_root"):
            context = self.local_git_root

        if (
            hasattr(self, "other_local_git_root")
            and context is not None
            and context == self.other_local_git_root
        ):
            subprocess.run(
                ["git", "fetch", "--all"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=context,
            )
            subprocess.run(
                ["git", "pull", "--all"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=context,
            )

        process = subprocess.run(
            ["git"] + cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=context
        )
        if process.returncode != 0:
            return ""

        result = ""
        if process.stderr:
            result += process.stderr.decode()

        if process.stdout:
            if result:
                result += "\n"

            result += process.stdout.decode()

        return result


class FakeAlpaBranchRepo(FakeAlpaRepo):
    def setup_method(self, method):
        super().setup_method(method)
        with open(f"{self.local_git_root}/.alpa.yaml", "a") as f:
            f.write("repo_type: branch\n")

        self.packages = ["je", "hele", "pikachu"]
        for package in self.packages:
            self.setup_package(package)

        self.local_repo = LocalRepoBranch(Path(self.local_git_root))

    def setup_package(self, package):
        self.git_cmd(["switch", "main"])
        self.git_cmd(["switch", "-c", package])
        with open(f"{self.local_git_root}/metadata.yaml", "w") as f:
            f.write(METADATA_CONFIG_MANDATORY_ONLY_KEYS)

        with open(f"{self.local_git_root}/{package}.spec", "w") as f:
            f.write(FAKE_SPEC_FILE)

        self.git_cmd(["add", "."])
        self.git_cmd(["commit", "-m", f"Add package {package}"])
        self.git_cmd(["push", "origin", package])
