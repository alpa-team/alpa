"""
Integration with alpa <-> upstream repo.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

import requests
from alpa_conf.metadata import Metadata
from click import ClickException

from alpa.repository import LocalRepo


class UpstreamIntegration(LocalRepo):
    def __init__(self, repo_path: Path) -> None:
        super().__init__(repo_path)
        self.metadata = Metadata(repo_path)
        self.nvr = f"{self.metadata.package_name}-{self.metadata.upstream_ref}"
        self.spec_file = f"{self.package}.spec"

    @staticmethod
    def _find_srpm_file_from_mock_build(srpm_result_dir: Path) -> Optional[Path]:
        for file_path in srpm_result_dir.iterdir():
            if file_path.name.endswith(".src.rpm"):
                return file_path

        return None

    def _mock_build_one_chroot(self, chroot: str, result_dir: Path) -> int:
        srpm_result_dir = result_dir / "srpm" / chroot
        process = subprocess.run(
            [
                "mock",
                "-r",
                chroot,
                "--buildsrpm",
                "--spec",
                self.spec_file,
                "--sources",
                f"{self.nvr}.tar.gz",
                "--resultdir",
                srpm_result_dir,
            ]
        )
        if process.returncode != 0:
            return process.returncode

        rpm_result_dir = result_dir / "build_results" / chroot
        srpm_path = UpstreamIntegration._find_srpm_file_from_mock_build(srpm_result_dir)
        if srpm_path is None:
            return 1

        process = subprocess.run(
            ["mock", "-r", chroot, "--resultdir", rpm_result_dir, srpm_path]
        )
        return process.returncode

    def _prepare_mock_result_dir(self, chroots: list[str]) -> Path:
        mock_results_path = self.repo_path / "mock_results"
        if mock_results_path.is_dir():
            # delete previous mock build
            shutil.rmtree(mock_results_path)

        for chroot in chroots:
            srpm_chroot_path = mock_results_path / "srpm" / chroot
            srpm_chroot_path.mkdir(parents=True)
            build_chroot_path = mock_results_path / "build_results" / chroot
            build_chroot_path.mkdir(parents=True)

        return mock_results_path

    def download_upstream_source(self) -> None:
        resp = requests.get(self.metadata.upstream_source_url, allow_redirects=True)
        if not resp.ok:
            raise ConnectionError(
                f"Couldn't download source from {self.metadata.upstream_source_url}. "
                f"Reason: {resp.reason}"
            )

        with open(f"{self.nvr}.tar.gz", "wb") as archive:
            archive.write(resp.content)

    def mockbuild(self, chroots: list[str]) -> None:
        self.download_upstream_source()
        root_mock_result_dir = self._prepare_mock_result_dir(chroots)

        for chroot in chroots:
            retval = self._mock_build_one_chroot(chroot, root_mock_result_dir)
            if retval != 0:
                raise ClickException(f"Mock returned non-zero value: {retval}")
