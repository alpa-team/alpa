from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from yaml import safe_load

from alpa_conf import AlpaRepoConfig, MetadataConfig
from test.constants import (
    METADATA_CONFIG_ALL_KEYS,
    ALPA_CONFIG_ALL_KEYS,
    METADATA_CONFIG_MANDATORY_ONLY_KEYS,
    ALPA_CONFIG_MANDATORY_KEYS,
)

from alpa.config.packit import PackitConfig


class TestPackitConfig:
    @pytest.mark.parametrize(
        "result, metadata_conf, alpa_conf",
        [
            pytest.param(
                {
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
                            "owner": "alpa-owner",
                            "project": "alpa-repo-pull-requests",
                        },
                        {
                            "job": "copr_build",
                            "trigger": "commit",
                            "branch": "uwu",
                            "targets": sorted(list({"f36", "f37", "centos"})),
                            "owner": "alpa-owner",
                            "project": "alpa-repo",
                        },
                    ],
                },
                METADATA_CONFIG_MANDATORY_ONLY_KEYS,
                ALPA_CONFIG_MANDATORY_KEYS,
            ),
            pytest.param(
                {
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
                            "owner": "alpa-owner",
                            "project": "alpa-repo-pull-requests",
                        },
                        {
                            "job": "copr_build",
                            "trigger": "commit",
                            "branch": "uwu",
                            "targets": sorted(list({"f36", "f37", "centos"})),
                            "owner": "alpa-owner",
                            "project": "alpa-repo",
                        },
                        {
                            "job": "copr_build",
                            "trigger": "commit",
                            "branch": "__alpa_autoupdate_uwu",
                            "targets": sorted(list({"f36", "f37", "centos"})),
                            "owner": "alpa-owner",
                            "project": "alpa-repo-pull-requests",
                        },
                    ],
                },
                METADATA_CONFIG_ALL_KEYS,
                ALPA_CONFIG_ALL_KEYS,
            ),
        ],
    )
    @patch.object(AlpaRepoConfig, "get_config")
    @patch.object(MetadataConfig, "get_config")
    def test_get_packit_config(
        self,
        mock_meta_get_config,
        mock_alpa_repo_get_config,
        result,
        metadata_conf,
        alpa_conf,
    ):
        mock_meta_get_config.return_value = MetadataConfig._fill_metadata_from_dict(
            safe_load(metadata_conf)
        )
        mock_alpa_repo_get_config.return_value = AlpaRepoConfig._config_from_dict(
            safe_load(alpa_conf)
        )

        packit_config = PackitConfig("uwu").get_packit_config()
        assert packit_config
        assert packit_config.get("jobs")
        for job in packit_config["jobs"]:
            assert job.get("targets")
            job["targets"] = sorted(list(job["targets"]))

        assert packit_config == result

    @pytest.mark.parametrize(
        "dir_content, result",
        [
            pytest.param(
                ["/some", "/thing", "/kakaka", "/home/user/.packit.yaml"], True
            ),
            pytest.param(["/some", "/thing", "/kakaka", "/home/user"], False),
        ],
    )
    @patch.object(AlpaRepoConfig, "get_config")
    @patch.object(MetadataConfig, "_load_metadata_config")
    @patch.object(Path, "is_file")
    @patch.object(Path, "iterdir")
    def test_packit_config_file_exists(
        self,
        mock_iterdir,
        mock_is_file,
        mock_load_metadata_config,
        mock_get_config,
        dir_content,
        result,
    ):
        mock_is_file.return_value = True
        mock_iterdir.return_value = [Path(path) for path in dir_content]

        mock_load_metadata_config.return_value = safe_load(METADATA_CONFIG_ALL_KEYS)
        mock_get_config.return_value = MagicMock()

        assert PackitConfig("uwu").packit_config_file_exists() == result
