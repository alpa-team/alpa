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
    "a forked form Alpa repository."
)

NO_WRITE_ACCESS_ERR = (
    "You don't have write access to this repository. If you "
    "want to create new package, please use `alpa request-package "
    "[PACKAGE NAME]` command instead."
)

NOT_IN_PREDEFINED_STATE = (
    "Repository is not in predefined state. Seems like someone "
    "was playing with it. Please see TODO LINK to return this repo "
    "back to its predefined state."
)

RETURNING_CLONE_URL_MSG = (
    "User {user} does not have access to {repo} repository. "
    "Using https url for cloning instead of ssh url."
)
