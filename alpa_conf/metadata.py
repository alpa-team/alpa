from os import getcwd
from pathlib import Path

from yaml import safe_load

from alpa_conf.constants import METADATA_FILE_NAMES, METADATA_SUFFIXES
from alpa_conf.exceptions import AlpaConfException


class Metadata:
    def __init__(self) -> None:
        self.working_dir = Path(getcwd())
        self.metadata = self._load_metadata_config()

        result, missing = Metadata._mandatory_fields_check(self.metadata)
        if not result:
            raise AlpaConfException(f"The `{missing}` key is missing in metadata.yaml")

    def _load_metadata_config(self) -> dict:
        config = {}
        for file_name, suffix in zip(METADATA_FILE_NAMES, METADATA_SUFFIXES):
            full_path = self.working_dir / f"{file_name}.{suffix}"
            if not full_path.is_file():
                continue

            with open(full_path) as meta_file:
                config = safe_load(meta_file.read())
                break

        if not config:
            raise FileNotFoundError("No metadata file found in package")

        return config

    @staticmethod
    def _mandatory_fields_check_rec(
        dict_to_test: dict, mandatory_keys: list
    ) -> tuple[bool, str]:
        for key_or_dict in mandatory_keys:
            if isinstance(key_or_dict, str):
                if key_or_dict not in dict_to_test.keys():
                    return False, key_or_dict
                else:
                    continue

            for key in key_or_dict.keys():
                if dict_to_test.get(key, None) is None:
                    return False, key

                result, missing = Metadata._mandatory_fields_check_rec(
                    dict_to_test[key], list(key_or_dict.values())[0]
                )
                if not result:
                    return False, missing

        return True, ""

    @classmethod
    def _mandatory_fields_check(cls, dict_to_test: dict) -> tuple[bool, str]:
        mandatory_keys = [
            "maintainers",
            "targets",
            "targets_notify_on_fail",
            {"upstream": ["url", "version"]},
        ]
        return cls._mandatory_fields_check_rec(dict_to_test, mandatory_keys)

    @property
    def maintainers(self) -> list[str]:
        return list(self.metadata["maintainers"].keys())

    @property
    def maintainer_email_dict(self) -> dict[str, str]:
        return self.metadata["maintainers"]

    @property
    def upstream_url(self) -> str:
        return self.metadata["upstream"]["url"]

    @property
    def upstream_version(self) -> str:
        return self.metadata["upstream"]["version"]

    @property
    def autoupdate(self) -> bool:
        return self.metadata.get("autoupdate", False)

    @property
    def targets(self) -> set[str]:
        return set(self.metadata["targets"])

    @property
    def targets_notify_on_fail(self) -> set[str]:
        return set(self.metadata.get("targets_notify_on_fail", []))

    @property
    def arch(self) -> set[str]:
        return set(self.metadata.get("arch", ["x86_64"]))
