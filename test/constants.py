METADATA_CONFIG_ALL_KEYS = """
name: some_package

autoupdate: true

maintainers:
  naruto: narutothebest@konoha.jp
  random_guy: 123@random.r

upstream:
  source_url: some-url
  ref: 1.1.1

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
