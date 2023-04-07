from os import getcwd
from pathlib import Path
from typing import Optional, NoReturn

from pydantic import EmailStr
from pydantic.dataclasses import dataclass
from yaml import safe_load

from alpa_conf.constants import METADATA_FILE_NAMES, METADATA_SUFFIXES
from alpa_conf.exceptions import AlpaConfException


@dataclass
class User:
    nick: str
    email: EmailStr


@dataclass
class Autoupdate:
    upstream_pkg_name: str
    anytia_backend: str  # TODO: anytia backend enum
    targets_notify_on_fail: set[str]


class MetadataConfig:
    def __init__(
        self,
        autoupdate: Optional[Autoupdate],
        maintainers: list[User],
        targets: set[str],
        arch: set[str],
    ) -> None:
        self.autoupdate = autoupdate
        self.maintainers = maintainers
        self.targets = targets
        self.arch = arch

    @staticmethod
    def _raise_missing_key(missing_key) -> NoReturn:
        raise AlpaConfException(f"The `{missing_key}` key is missing in metadata.yaml")

    @staticmethod
    def _fill_autoupdate_dataclass(d: dict) -> Autoupdate:
        targets_notify_on_fail = set(d.pop("targets_notify_on_fail", []))
        return Autoupdate(**d, targets_notify_on_fail=targets_notify_on_fail)

    @classmethod
    def _fill_metadata_from_dict(cls, d: dict) -> "MetadataConfig":
        autoupdate = d.get("autoupdate")
        autoupdate_dataclass = None
        if autoupdate is not None:
            autoupdate_dataclass = cls._fill_autoupdate_dataclass(autoupdate)

        users_list = []
        maintainers = d.get("maintainers")
        if maintainers is None:
            cls._raise_missing_key("maintainers")

        for maintainer_dict in maintainers:
            maintainer = maintainer_dict.get("user")
            if maintainer is None:
                cls._raise_missing_key("maintainers.user")

            users_list.append(User(**maintainer))

        targets = d.get("targets")
        if targets is None:
            cls._raise_missing_key("targets")

        return MetadataConfig(
            autoupdate=autoupdate_dataclass,
            maintainers=users_list,
            targets=set(targets),
            arch=set(d.get("arch", ["x86_64"])),
        )

    @classmethod
    def _load_metadata_config(cls, working_dir: Path) -> Optional["MetadataConfig"]:
        for file_name in METADATA_FILE_NAMES:
            for suffix in METADATA_SUFFIXES:
                full_path = working_dir / f"{file_name}.{suffix}"
                if not full_path.is_file():
                    continue

                with open(full_path) as meta_file:
                    return cls._fill_metadata_from_dict(safe_load(meta_file.read()))

        return None

    @classmethod
    def get_config(cls, working_dir: Optional[Path] = None) -> "MetadataConfig":
        if working_dir is None:
            working_dir = Path(getcwd())

        metadata_data_class = cls._load_metadata_config(working_dir)
        if metadata_data_class is None:
            raise FileNotFoundError("No metadata file found in package")

        return metadata_data_class
