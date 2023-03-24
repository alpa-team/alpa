METADATA_CONFIG_ALL_KEYS = """
autoupdate: true

maintainers:
  naruto: narutothebest@konoha.jp
  random_guy: 123@random.r

upstream:
  url: some-url
  version: 1.1.1

targets:
  - f37
  - f36
  - centos

targets_notify_on_fail:
  - f36
  - centos

arch:
  - x86_64
  - s390x
"""

METADATA_CONFIG_MANDATORY_ONLY_KEYS = """
maintainers:
  naruto: narutothebest@konoha.jp
  random_guy: 123@random.r

upstream:
  url: some-url
  version: 1.1.1

targets:
  - f37
  - f36
  - centos

targets_notify_on_fail:
  - f36
  - centos
"""
