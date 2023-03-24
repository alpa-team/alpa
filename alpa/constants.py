from enum import Enum


UPSTREAM_NAME = "upstream"
ORIGIN_NAME = "origin"
MAIN_BRANCH = "main"


GH_API_TOKEN_NAME = "ALPA_GH_API_TOKEN"
GH_WRITE_ACCESS = ["admin", "write"]

ALPA_ISSUE_REPO_NAME = "issue-repo"
ALPA_FEAT_BRANCH_PREFIX = "__feat_"
ALPA_FEAT_BRANCH = ALPA_FEAT_BRANCH_PREFIX + "{pkgname}"

GLOBAL_CFG_FILE = "/etc/vem.cfg"
USER_CFG_FILE = "~/.config/vem.cfg"
# order is important! user cfg overrides global cfg
CONFIG_FILE_LOCATIONS = [USER_CFG_FILE, GLOBAL_CFG_FILE]


class PackageRequest(str, Enum):
    TITLE = "[alpa] New request for package {package_name}"
    BODY = "@{user} requested {package_name} for repo {repo_name}"
    LABEL = "request"
