from enum import Enum


UPSTREAM_NAME = "upstream"
ORIGIN_NAME = "origin"
MAIN_BRANCH = "main"


GH_API_TOKEN_NAME = "ALPA_GH_API_TOKEN"
GH_WRITE_ACCESS = ["admin", "write"]

ALPA_ISSUE_REPO_NAME = "issue-repo"
ALPA_FEAT_BRANCH_PREFIX = "__feat_"
ALPA_FEAT_BRANCH = ALPA_FEAT_BRANCH_PREFIX + "{pkgname}"

GLOBAL_CFG_FILE = "/etc/alpa.yaml"
USER_CFG_FILE = "~/.config/alpa.yaml"
# order is important! user cfg overrides global cfg
CONFIG_FILE_LOCATIONS = [USER_CFG_FILE, GLOBAL_CFG_FILE]

PACKIT_CONFIG_NAMES = [
    ".packit.yaml",
    ".packit.yml",
    ".packit.json",
    "packit.yaml",
    "packit.yml",
    "packit.json",
]

METADATA_FILE_NAMES = [
    ".metadata.yaml",
    ".metadata.yml",
    "metadata.yaml",
    "metadata.yml",
]

ALPA_CONFIG_FILE_NAMES = [".alpa.yaml", ".alpa.yml", "alpa.yaml", "alpa.yml"]

REQUEST_LABEL = "request"
CREATE_PACKAGE_REQUEST_TITLE = (
    "[alpa request-new-package] New request to create a package {package_name}"
)
DELETE_PACKAGE_REQUEST_TITLE = (
    "[alpa delete-package] New request to delete a package {package_name}"
)


class RequestEnum(str, Enum):
    delete = "delete"
    create = "create"
