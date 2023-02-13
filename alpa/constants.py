from enum import Enum


UPSTREAM_NAME = "upstream"
ORIGIN_NAME = "origin"
MAIN_BRANCH = "main"


GH_API_TOKEN_NAME = "FAP_GH_API_TOKEN"
GH_WRITE_ACCESS = ["admin", "write"]

FAP_ISSUE_REPO_NAME = "issue-repo"
FAP_FEAT_BRANCH_PREFIX = "__feat_"
FAP_FEAT_BRANCH = FAP_FEAT_BRANCH_PREFIX + "{pkgname}"


class PackageRequest(str, Enum):
    TITLE = "[alpa] New request for package {package_name}"
    BODY = "@{user} requested {package_name} for repo {repo_name}"
    LABEL = "request"
