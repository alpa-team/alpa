"""
File for really long messages.
"""


NO_GH_API_KEY_FOUND = (
    "No GitHub API key found. Please set the "
    "{token} environment variable and pass "
    "the GitHub API token to it. For more information please "
    "see (link TODO)"
)

CLONED_REPO_IS_NOT_FORK = (
    "The url of GitHub repository isn't fork "
    "(does not have upstream). Please provide repository which is "
    "a forked form Fedora Alternative Packaging repository."
)

NO_WRITE_ACCESS_ERR = (
    "You don't have write access to this repository. If you "
    "want to create new package, please use `alpa request-package "
    "[PACKAGE NAME]` command instead."
)
