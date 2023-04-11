"""
Integration with alpa <-> upstream repo.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

import click
import requests
from alpa.config import MetadataConfig
from click import ClickException
from specfile import Specfile

from alpa.repository.branch import LocalRepoBranch


class UpstreamIntegration(LocalRepoBranch):
    def __init__(self, repo_path: Path) -> None:
        super().__init__(repo_path)
        self.metadata = MetadataConfig.get_config(repo_path)
        self.specfile = Specfile(Path(repo_path / f"{self.package}.spec"))
        self.name_version = (
            f"{self.specfile.expanded_name}-{self.specfile.expanded_version}"
        )
        self.nvr = f"{self.name_version}-{self.specfile.expanded_release}"

    @staticmethod
    def _find_srpm_file_from_mock_build(srpm_result_dir: Path) -> Optional[Path]:
        for file_path in srpm_result_dir.iterdir():
            if file_path.name.endswith(".src.rpm"):
                return file_path

        return None

    @staticmethod
    def _run_mock_command(cmd: list[str]) -> int:
        click.echo(f"Executing command {' '.join(cmd)}")
        return subprocess.run(cmd).returncode

    def _mock_build_one_chroot(
        self, chroot: str, result_dir: Path, source_file_name: str
    ) -> int:
        srpm_result_dir = result_dir / "srpm" / chroot
        retval = UpstreamIntegration._run_mock_command(
            [
                "mock",
                "-r",
                chroot,
                "--buildsrpm",
                "--spec",
                self.specfile.path.name,
                "--sources",
                f"{source_file_name}.tar.gz",
                "--resultdir",
                str(srpm_result_dir),
            ]
        )
        if retval != 0:
            return retval

        rpm_result_dir = result_dir / "build_results" / chroot
        srpm_path = UpstreamIntegration._find_srpm_file_from_mock_build(srpm_result_dir)
        if srpm_path is None:
            return 1

        return UpstreamIntegration._run_mock_command(
            ["mock", "-r", chroot, "--resultdir", str(rpm_result_dir), str(srpm_path)]
        )

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

    @staticmethod
    def download_upstream_source(upstream_source_url: str, name_version: str) -> None:
        resp = requests.get(upstream_source_url, allow_redirects=True)
        if not resp.ok:
            raise ConnectionError(
                f"Couldn't download source from {upstream_source_url}. "
                f"Reason: {resp.reason}"
            )

        with open(f"{name_version}.tar.gz", "wb") as archive:
            archive.write(resp.content)

    def mockbuild(self, chroots: list[str]) -> None:
        with self.specfile.sources() as sources:
            source0 = min(sources, key=lambda src: src.number)

        source_file_name = source0.expanded_filename.rstrip(".tar.gz")
        self.download_upstream_source(source0.expanded_location, source_file_name)
        root_mock_result_dir = self._prepare_mock_result_dir(chroots)

        for chroot in chroots:
            retval = self._mock_build_one_chroot(
                chroot, root_mock_result_dir, source_file_name
            )
            if retval != 0:
                raise ClickException(f"Mock returned non-zero value: {retval}")
