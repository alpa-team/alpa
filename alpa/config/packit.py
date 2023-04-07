from os import getcwd
from pathlib import Path

from yaml import dump

from alpa_conf import AlpaRepoConfig, MetadataConfig

from alpa.constants import PACKIT_CONFIG_NAMES


class PackitConfig:
    def __init__(self, package_name: str) -> None:
        self.package_name = package_name
        self.working_dir = Path(getcwd())
        self.metadata = MetadataConfig.get_config(self.working_dir)
        self.alpa_repo_config = AlpaRepoConfig.get_config()

    def get_packit_config(self) -> dict:
        return {
            "specfile_path": f"{self.package_name}.spec",
            "srpm_build_deps": ["pip"],
            "actions": {
                "create-archive": [
                    "pip install pyalpa",
                    'bash -c "alpa get-pkg-archive"',
                    f'bash -c "ls -1 ./{self.package_name}-*.tar.gz"',
                ],
            },
            "jobs": [
                {
                    "job": "copr_build",
                    "trigger": "pull_request",
                    "targets": list(self.metadata.targets),
                    "owner": self.alpa_repo_config.copr_owner,
                    "project": f"{self.alpa_repo_config.copr_repo}-pull-requests",
                },
                {
                    "job": "copr_build",
                    "trigger": "commit",
                    "branch": self.package_name,
                    "targets": list(self.metadata.targets),
                    "owner": self.alpa_repo_config.copr_owner,
                    "project": self.alpa_repo_config.copr_repo,
                },
            ],
        }

    def packit_config_file_exists(self) -> bool:
        for packit_config_name in PACKIT_CONFIG_NAMES:
            files_in_dir = [
                file.name for file in self.working_dir.iterdir() if file.is_file()
            ]
            if packit_config_name in files_in_dir:
                return True

        return False

    def create_packit_config(self) -> None:
        if self.packit_config_file_exists():
            raise FileExistsError("Packit configuration file already exists")

        with open(".packit.yaml", "w") as packit_yaml:
            packit_yaml.write(dump(self.get_packit_config(), sort_keys=False))
