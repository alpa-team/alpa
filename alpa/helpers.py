import requests
from alpa_conf.metadata import Metadata


def download_upstream_source() -> None:
    metadata = Metadata()
    resp = requests.get(metadata.upstream_url, allow_redirects=True)
    if not resp.ok:
        raise ConnectionError(
            f"Couldn't download source from {metadata.upstream_url}. "
            f"Reason: {resp.reason}"
        )

    with open(
        f"{metadata.package_name}-{metadata.upstream_version}.tar.gz", "wb"
    ) as archive:
        archive.write(resp.content)
