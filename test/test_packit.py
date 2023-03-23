from pathlib import Path
from unittest.mock import patch

import pytest
from yaml import safe_load

from alpa_conf.metadata import Metadata
from alpa_conf.packit import PackitConfig
from test.config import METADATA_CONFIG_ALL_KEYS


class TestPackitConfig:
    @patch.object(Metadata, "_mandatory_fields_check")
    @patch.object(Metadata, "_load_metadata_config")
    def test_get_packit_config(
        self, mock_load_metadata_config, mock_mandatory_fields_check
    ):
        mock_load_metadata_config.return_value = safe_load(METADATA_CONFIG_ALL_KEYS)
        mock_mandatory_fields_check.return_value = True, ""

        assert PackitConfig("uwu").get_packit_config() == {
            "specfile_path": ".spec",
            "jobs": [
                {
                    "job": "copr_build",
                    "trigger": "pull_request",
                    "targets": {"f36", "f37", "centos"},
                },
                {
                    "job": "copr_build",
                    "trigger": "commit",
                    "branch": "uwu",
                    "targets": {"f36", "f37", "centos"},
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
    @patch.object(Metadata, "_mandatory_fields_check")
    @patch.object(Metadata, "_load_metadata_config")
    @patch.object(Path, "is_file")
    @patch.object(Path, "iterdir")
    def test_packit_config_file_exists(
        self,
        mock_iterdir,
        mock_is_file,
        mock_load_metadata_config,
        mock_mandatory_fields_check,
        dir_content,
        result,
    ):
        mock_is_file.return_value = True
        mock_iterdir.return_value = [Path(path) for path in dir_content]

        mock_load_metadata_config.return_value = safe_load(METADATA_CONFIG_ALL_KEYS)
        mock_mandatory_fields_check.return_value = True, ""

        assert PackitConfig("uwu")._packit_config_file_exists() == result
