METADATA_FILE_NAMES = [".metadata", "metadata"]
METADATA_SUFFIXES = ["yaml", "yml"]

PACKIT_CONFIG_NAMES = [
    ".packit.yaml",
    ".packit.yml",
    ".packit.json",
    "packit.yaml",
    "packit.yml",
    "packit.json",
]

MANDATORY_KEYS = [
    "maintainers",
    "targets",
    "targets_notify_on_fail",
    {"upstream": ["source_url", "ref"]},
]
