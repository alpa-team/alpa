from pathlib import Path
from typing import Optional

import requests
from alpa_conf.metadata import Metadata


def download_upstream_source(root_repo_path: Optional[Path] = None) -> None:
    metadata = Metadata(root_repo_path)
    resp = requests.get(metadata.upstream_source_url, allow_redirects=True)
    if not resp.ok:
        raise ConnectionError(
            f"Couldn't download source from {metadata.upstream_source_url}. "
            f"Reason: {resp.reason}"
        )

    with open(
        f"{metadata.package_name}-{metadata.upstream_ref}.tar.gz", "wb"
    ) as archive:
        archive.write(resp.content)
