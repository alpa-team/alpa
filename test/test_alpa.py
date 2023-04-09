from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from yaml import safe_load

from alpa_conf.alpa import AlpaRepoConfig
from alpa_conf.exceptions import AlpaConfException
from test.config import ALPA_CONFIG_MANDATORY_KEYS, ALPA_CONFIG_ALL_KEYS


class TestAlpa:
    @pytest.mark.parametrize(
        "d",
        [
            pytest.param(safe_load(ALPA_CONFIG_MANDATORY_KEYS)),
            pytest.param(safe_load(ALPA_CONFIG_ALL_KEYS)),
        ],
    )
    def test_config_from_dict(self, d):
        AlpaRepoConfig._config_from_dict(d)

    @pytest.mark.parametrize(
        "d, missing",
        [
            pytest.param(
                {
                    "repo_type": "branch",
                    "copr_owner": "uwu",
                },
                "copr_repo",
            ),
            pytest.param(
                {
                    "copr_owner": "uwu",
                    "copr_repo": "haha",
                },
                "repo_type",
            ),
        ],
    )
    def test_config_from_dict_fail(self, d, missing):
        with pytest.raises(AlpaConfException, match=missing):
            AlpaRepoConfig._config_from_dict(d)

    @pytest.mark.parametrize(
        "d",
        [
            pytest.param(
                {
                    "repo_type": "something-bad",
                    "copr_owner": "uwu",
                    "copr_repo": "haha",
                }
            )
        ],
    )
    def test_config_from_dict_bad_repo_type(self, d):
        with pytest.raises(KeyError):
            AlpaRepoConfig._config_from_dict(d)

    @pytest.mark.parametrize(
        "alpa_config, path, result",
        [
            pytest.param(ALPA_CONFIG_ALL_KEYS, "/test/.alpa.yaml", True),
            pytest.param(ALPA_CONFIG_MANDATORY_KEYS, "/test/not-alpa-file", False),
        ],
    )
    def test_load_alpa_config(self, fs: FakeFilesystem, alpa_config, path, result):
        fs.create_file(path, contents="test")

        with patch("builtins.open", mock_open(read_data=alpa_config)):
            ret = AlpaRepoConfig._load_alpa_config(Path("/test"))

        if result:
            assert ret is not None
        else:
            assert ret is None

    @pytest.mark.parametrize(
        "alpa_config",
        [
            pytest.param(ALPA_CONFIG_ALL_KEYS),
            pytest.param(ALPA_CONFIG_MANDATORY_KEYS),
        ],
    )
    @patch.object(AlpaRepoConfig, "_load_alpa_config")
    def test_content_in_config_file(self, mock_load_alpa_config, alpa_config):
        mock_load_alpa_config.return_value = AlpaRepoConfig._config_from_dict(
            safe_load(alpa_config)
        )

        config = AlpaRepoConfig.get_config()
        assert config.repo_type == "branch"
        assert config.copr_owner == "alpa-owner"
        assert config.copr_repo == "alpa-repo"
        if "allow_foreign_contributing:" in alpa_config:
            assert config.allow_foreign_contributing
        else:
            assert not config.allow_foreign_contributing
