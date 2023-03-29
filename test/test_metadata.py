from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from yaml import safe_load

from alpa_conf.constants import MANDATORY_KEYS
from alpa_conf.metadata import Metadata
from test.config import METADATA_CONFIG_ALL_KEYS, METADATA_CONFIG_MANDATORY_ONLY_KEYS


class TestMetadata:
    @pytest.mark.parametrize(
        "metadata_config, path, result",
        [
            pytest.param(METADATA_CONFIG_ALL_KEYS, "/test/.metadata.yaml", True),
            pytest.param(
                METADATA_CONFIG_MANDATORY_ONLY_KEYS, "/test/not-metadata-file", False
            ),
        ],
    )
    def test_load_metadata_config(
        self, fs: FakeFilesystem, metadata_config, path, result
    ):
        fs.create_file(path, contents="test")
        metadata_instance = MagicMock(working_dir=Path("/test"))

        with patch("builtins.open", mock_open(read_data=metadata_config)):
            ret = Metadata._load_metadata_config(metadata_instance)

        if result:
            assert ret
        else:
            assert not ret

    @pytest.mark.parametrize(
        "dict_to_test, result",
        [
            pytest.param(
                {
                    "name": ...,
                    "maintainers": ...,
                    "targets": ...,
                    "targets_notify_on_fail": ...,
                    "upstream": {"source_url": ..., "ref": ...},
                },
                True,
            ),
            pytest.param(
                {"maintainers": ..., "targets": ..., "targets_notify_on_fail": ...},
                False,
            ),
        ],
    )
    def test_mandatory_fields_check(self, dict_to_test, result):
        res, _ = Metadata._mandatory_fields_check(dict_to_test)
        assert res == result

    @patch.object(Metadata, "_mandatory_fields_check")
    @patch.object(Metadata, "_load_metadata_config")
    def test_maintainers(self, mock_load_metadata_config, mock_mandatory_fields_check):
        mock_load_metadata_config.return_value = safe_load(METADATA_CONFIG_ALL_KEYS)
        mock_mandatory_fields_check.return_value = True, ""

        assert Metadata().maintainers == ["naruto", "random_guy"]

    @pytest.mark.parametrize(
        "metadata_config",
        [
            pytest.param(METADATA_CONFIG_ALL_KEYS),
            pytest.param(METADATA_CONFIG_MANDATORY_ONLY_KEYS),
        ],
    )
    @patch.object(Metadata, "_mandatory_fields_check")
    @patch.object(Metadata, "_load_metadata_config")
    def test_content_in_config_file(
        self, mock_load_metadata_config, mock_mandatory_fields_check, metadata_config
    ):
        mock_load_metadata_config.return_value = safe_load(metadata_config)
        mock_mandatory_fields_check.return_value = True, ""

        metadata_cls = Metadata()

        assert metadata_cls.maintainer_email_dict == {
            "naruto": "narutothebest@konoha.jp",
            "random_guy": "123@random.r",
        }
        assert metadata_cls.upstream_source_url == "some-url"
        assert metadata_cls.upstream_ref == "1.1.1"
        assert metadata_cls.targets == {"f36", "f37", "centos"}
        assert metadata_cls.targets_notify_on_fail == {"f36", "centos"}

        if "autoupdate:" in metadata_config:
            assert metadata_cls.autoupdate
        else:
            assert not metadata_cls.autoupdate

        if "arch:" in metadata_config:
            assert metadata_cls.arch == {"x86_64", "s390x"}
        else:
            assert metadata_cls.arch == {"x86_64"}

    def test_be_aware_of_changes_in_mandatory_keys(self):
        assert [
            "maintainers",
            "targets",
            "targets_notify_on_fail",
            {"upstream": ["source_url", "ref"]},
        ] == MANDATORY_KEYS
