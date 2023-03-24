from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest
from yaml import safe_load

from alpa_conf.metadata import Metadata
from test.config import METADATA_CONFIG_ALL_KEYS, METADATA_CONFIG_MANDATORY_ONLY_KEYS


class TestMetadata:
    @pytest.mark.parametrize(
        "metadata_config, is_file_ret",
        [
            pytest.param(METADATA_CONFIG_ALL_KEYS, True),
            pytest.param(METADATA_CONFIG_MANDATORY_ONLY_KEYS, True),
            pytest.param(METADATA_CONFIG_MANDATORY_ONLY_KEYS, False),
        ],
    )
    @patch.object(Path, "is_file")
    def test_load_metadata_config(self, mock_is_file, metadata_config, is_file_ret):
        mock_is_file.return_value = is_file_ret
        metadata_instance = MagicMock(working_dir=Path("/home/user"))

        ret = None
        with patch("builtins.open", mock_open(read_data=metadata_config)):
            if is_file_ret:
                ret = Metadata._load_metadata_config(metadata_instance)
            else:
                with pytest.raises(FileNotFoundError):
                    ret = Metadata._load_metadata_config(metadata_instance)

        if is_file_ret:
            assert ret is not None
        else:
            assert ret is None

    @pytest.mark.parametrize(
        "dict_to_test, result",
        [
            pytest.param(
                {
                    "name": ...,
                    "maintainers": ...,
                    "targets": ...,
                    "targets_notify_on_fail": ...,
                    "upstream": {"url": ..., "version": ...},
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
        assert metadata_cls.package_name == "pretty_package"
        assert metadata_cls.upstream_url == "some-url"
        assert metadata_cls.upstream_version == "1.1.1"
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
