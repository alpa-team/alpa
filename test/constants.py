METADATA_CONFIG_ALL_KEYS = """
---
autoupdate:
  upstream_pkg_name: some_package
  anytia_backend: pypi

  targets_notify_on_fail:
    - f36
    - centos

maintainers:
  - user:
      nick: naruto
      email: narutothebest@konoha.jp
  - user:
      nick: random_guy
      email: 123@random.r

targets:
  - f37
  - f36
  - centos

arch:
  - x86_64
  - s390x
"""


METADATA_CONFIG_MANDATORY_ONLY_KEYS = """
---
maintainers:
  - user:
      nick: naruto
      email: narutothebest@konoha.jp
  - user:
      nick: random_guy
      email: 123@random.r

targets:
  - f37
  - f36
  - centos
"""


METADATA_WITHOUT_TARGETS = """
---
maintainers:
  - user:
      nick: naruto
      email: narutothebest@konoha.jp
  - user:
      nick: random_guy
      email: 123@random.r
"""


ALPA_CONFIG_MANDATORY_KEYS = """
---
repo_type: branch
copr_owner: alpa-owner
copr_repo: alpa-repo
"""


ALPA_CONFIG_ALL_KEYS = """
---
repo_type: branch
copr_owner: alpa-owner
copr_repo: alpa-repo
allow_foreign_contributing: true

targets:
  - f32

arch:
  - aarch64
"""
