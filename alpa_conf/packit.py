from os import getcwd
from pathlib import Path

from yaml import dump

from alpa_conf.constants import PACKIT_CONFIG_NAMES
from alpa_conf.metadata import Metadata


class PackitConfig:
    def __init__(self, package_name: str) -> None:
        self.package_name = package_name
        self.working_dir = Path(getcwd())
        self.metadata = Metadata()

    def get_packit_config(self) -> dict:
        return {
            "specfile_path": ".spec",
            "jobs": [
                {
                    "job": "copr_build",
                    "trigger": "pull_request",
                    "targets": self.metadata.targets,
                },
                {
                    "job": "copr_build",
                    "trigger": "commit",
                    "branch": self.package_name,
                    "targets": self.metadata.targets,
                },
            ],
        }

    def _packit_config_file_exists(self) -> bool:
        for packit_config_name in PACKIT_CONFIG_NAMES:
            files_in_dir = [
                file.name for file in self.working_dir.iterdir() if file.is_file()
            ]
            if packit_config_name in files_in_dir:
                return True

        return False

    def create_packit_config(self) -> None:
        if self._packit_config_file_exists():
            raise FileExistsError("Packit configuration file already exists")

        with open(".packit.yaml", "w") as packit_yaml:
            packit_yaml.write(dump(self.get_packit_config()))
