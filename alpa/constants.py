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


class PackageRequest(str, Enum):
    TITLE = "[alpa] New request for package {package_name}"
    BODY = "@{user} requested {package_name} for repo {repo_name}"
    LABEL = "request"
