from pathlib import Path
from unittest.mock import patch

import pytest
from yaml import safe_load

from alpa_conf import MetadataConfig
from test.constants import METADATA_CONFIG_ALL_KEYS

from alpa.config.packit import PackitConfig


class TestPackitConfig:
    @patch.object(MetadataConfig, "get_config")
    def test_get_packit_config(self, mock_get_config):
        mock_get_config.return_value = MetadataConfig._fill_metadata_from_dict(
            safe_load(METADATA_CONFIG_ALL_KEYS)
        )
        packit_config = PackitConfig("uwu").get_packit_config()
        assert packit_config
        assert packit_config.get("jobs")
        for job in packit_config["jobs"]:
            assert job.get("targets")
            job["targets"] = sorted(list(job["targets"]))

        assert packit_config == {
            "specfile_path": "uwu.spec",
            "srpm_build_deps": ["pip"],
            "actions": {
                "create-archive": [
                    "pip install pyalpa",
                    'bash -c "alpa get-pkg-archive"',
                    'bash -c "ls -1 ./uwu-*.tar.gz"',
                ],
            },
            "jobs": [
                {
                    "job": "copr_build",
                    "trigger": "pull_request",
                    "targets": sorted(list({"f36", "f37", "centos"})),
                },
                {
                    "job": "copr_build",
                    "trigger": "commit",
                    "branch": "uwu",
                    "targets": sorted(list({"f36", "f37", "centos"})),
                },
            ],
        }

    @pytest.mark.parametrize(
        "dir_content, result",
        [
            pytest.param(
                ["/some", "/thing", "/kakaka", "/home/user/.packit.yaml"], True
            ),
            pytest.param(["/some", "/thing", "/kakaka", "/home/user"], False),
        ],
    )
    @patch.object(MetadataConfig, "_load_metadata_config")
    @patch.object(Path, "is_file")
    @patch.object(Path, "iterdir")
    def test_packit_config_file_exists(
        self,
        mock_iterdir,
        mock_is_file,
        mock_load_metadata_config,
        dir_content,
        result,
    ):
        mock_is_file.return_value = True
        mock_iterdir.return_value = [Path(path) for path in dir_content]

        mock_load_metadata_config.return_value = safe_load(METADATA_CONFIG_ALL_KEYS)

        assert PackitConfig("uwu").packit_config_file_exists() == result
