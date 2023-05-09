from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
from pydantic.dataclasses import dataclass
from pyfakefs.fake_filesystem import FakeFilesystem
from yaml import safe_load

from alpa.config.alpa_repo import AlpaRepoType, AlpaRepoConfig
from alpa.exceptions import AlpaConfException
from alpa.config.metadata import MetadataConfig, User
from test.constants import (
    METADATA_CONFIG_ALL_KEYS,
    METADATA_CONFIG_MANDATORY_ONLY_KEYS,
    METADATA_WITHOUT_TARGETS,
)


class TestMetadata:
    @pytest.mark.parametrize(
        "d",
        [
            pytest.param(
                {
                    "upstream_pkg_name": "some_package",
                    "anytia_backend": "pypi",
                    "targets_notify_on_fail": ["f36", "centos"],
                }
            ),
            pytest.param(
                {
                    "upstream_pkg_name": "some_package",
                    "anytia_backend": "pypi",
                }
            ),
        ],
    )
    def test_fill_autoupdate_dataclass(self, d):
        result = MetadataConfig._fill_autoupdate_dataclass(d)
        assert result.upstream_pkg_name == "some_package"
        assert result.anytia_backend == "pypi"
        if result.targets_notify_on_fail:
            assert result.targets_notify_on_fail == {"f36", "centos"}

    @pytest.mark.parametrize(
        "d, missing",
        [
            pytest.param({"upstream_pkg_name": "some_package"}, "anytia_backend"),
            pytest.param({"anytia_backend": "pypi"}, "upstream_pkg_name"),
        ],
    )
    def test_fill_autoupdate_dataclass_fail(self, d, missing):
        with pytest.raises(TypeError, match=missing):
            MetadataConfig._fill_autoupdate_dataclass(d)

    @pytest.mark.parametrize(
        "raw_yaml",
        [
            pytest.param(METADATA_CONFIG_ALL_KEYS),
            pytest.param(METADATA_CONFIG_MANDATORY_ONLY_KEYS),
        ],
    )
    @patch.object(AlpaRepoConfig, "get_config")
    def test_fill_metadata_from_dict_runs(self, mock_get_config, raw_yaml):
        mock_get_config.return_value = AlpaRepoConfig(
            repo_type=AlpaRepoType.branch, copr_owner="owner", copr_repo="repo"
        )

        MetadataConfig._fill_metadata_from_dict(safe_load(raw_yaml))

    @pytest.mark.parametrize(
        "d, missing",
        [
            pytest.param({"targets": ["f37", "f38"]}, "maintainers"),
            pytest.param(
                {
                    "maintainers": [
                        {"user": {"nick": "naruto", "email": "narutothebest@konoha.jp"}}
                    ]
                },
                "targets",
            ),
            pytest.param(
                {
                    "maintainers": [{}],
                    "targets": ["f33"],
                },
                "maintainers.user",
            ),
        ],
    )
    @patch.object(AlpaRepoConfig, "get_config")
    def test_fill_metadata_from_dict_fail(self, mock_get_config, d, missing):
        mock_get_config.return_value = AlpaRepoConfig(
            repo_type=AlpaRepoType.branch, copr_owner="owner", copr_repo="repo"
        )

        with pytest.raises(AlpaConfException, match=missing):
            MetadataConfig._fill_metadata_from_dict(d)

    @pytest.mark.parametrize(
        "metadata_config, path, result",
        [
            pytest.param(METADATA_CONFIG_ALL_KEYS, "/test/.metadata.yaml", True),
            pytest.param(
                METADATA_CONFIG_MANDATORY_ONLY_KEYS, "/test/not-metadata-file", False
            ),
        ],
    )
    @patch.object(AlpaRepoConfig, "get_config")
    def test_load_metadata_config(
        self, mock_get_config, fs: FakeFilesystem, metadata_config, path, result
    ):
        mock_get_config.return_value = AlpaRepoConfig(
            repo_type=AlpaRepoType.branch, copr_owner="owner", copr_repo="repo"
        )

        fs.create_file(path, contents="test")

        with patch("builtins.open", mock_open(read_data=metadata_config)):
            ret = MetadataConfig._load_metadata_config(Path("/test"))

        if result:
            assert ret is not None
        else:
            assert ret is None

    @pytest.mark.parametrize(
        "metadata_config",
        [
            pytest.param(METADATA_CONFIG_ALL_KEYS),
            pytest.param(METADATA_CONFIG_MANDATORY_ONLY_KEYS),
        ],
    )
    @patch.object(MetadataConfig, "_load_metadata_config")
    @patch.object(AlpaRepoConfig, "get_config")
    def test_content_in_config_file(
        self, mock_get_config, mock_load_metadata_config, metadata_config
    ):
        mock_get_config.return_value = AlpaRepoConfig(
            repo_type=AlpaRepoType.branch, copr_owner="owner", copr_repo="repo"
        )

        mock_load_metadata_config.return_value = (
            MetadataConfig._fill_metadata_from_dict(safe_load(metadata_config))
        )

        metadata = MetadataConfig.get_config()

        @dataclass
        class UserCmp(User):
            def __eq__(self, other):
                return self.nick == other.nick and self.email == other.email

        maintainers_cmp = [
            UserCmp(user.nick, user.email) for user in metadata.maintainers
        ]
        assert maintainers_cmp[0] == UserCmp(
            nick="naruto", email="narutothebest@konoha.jp"
        )
        assert maintainers_cmp[1] == UserCmp(nick="random_guy", email="123@random.r")

        assert metadata.targets == {"f36", "f37", "centos"}

        if "autoupdate:" in metadata_config:
            assert metadata.autoupdate is not None
            assert metadata.autoupdate.upstream_pkg_name == "some_package"
            assert metadata.autoupdate.anytia_backend == "pypi"
            assert metadata.autoupdate.targets_notify_on_fail == {"f36", "centos"}
        else:
            assert metadata.autoupdate is None

        if "arch:" in metadata_config:
            assert metadata.arch == {"x86_64", "s390x"}
        else:
            assert metadata.arch == {"x86_64"}

    @pytest.mark.parametrize(
        "metadata_config",
        [
            pytest.param(METADATA_CONFIG_ALL_KEYS),
            pytest.param(METADATA_CONFIG_MANDATORY_ONLY_KEYS),
            pytest.param(METADATA_WITHOUT_TARGETS),
        ],
    )
    @patch.object(MetadataConfig, "_load_metadata_config")
    @patch.object(AlpaRepoConfig, "get_config")
    def test_content_in_config_file_with_alpa_repo_having_chroot_specified(
        self, mock_get_config, mock_load_metadata_config, metadata_config
    ):
        mock_get_config.return_value = AlpaRepoConfig(
            repo_type=AlpaRepoType.branch,
            copr_owner="owner",
            copr_repo="repo",
            targets={"f33"},
            arch={"aarch64"},
        )

        mock_load_metadata_config.return_value = (
            MetadataConfig._fill_metadata_from_dict(safe_load(metadata_config))
        )

        metadata = MetadataConfig.get_config()

        if "targets:" in metadata_config:
            assert metadata.targets == {"f33", "f36", "f37", "centos"}
        else:
            assert metadata.targets == {"f33"}

        if "arch:" in metadata_config:
            assert metadata.arch == {"x86_64", "s390x", "aarch64"}
        else:
            assert metadata.arch == {"aarch64"}

    def test_chroots(self):
        config = MetadataConfig(
            autoupdate=None,
            maintainers=[],
            targets={"fedora-37", "centos"},
            arch={"s390x", "aarch64"},
        )

        assert sorted(config.chroots) == sorted(
            ["fedora-37-s390x", "centos-s390x", "fedora-37-aarch64", "centos-aarch64"]
        )
