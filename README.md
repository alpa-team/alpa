## Alpa

Another cooL way to PAckage in copr

### Status of alpa system

| Package   | Copr build status                                                                                                                                                                                                     |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| alpa      | [![Copr build status](https://copr.fedorainfracloud.org/coprs/alpa-team/alpa/package/alpa/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/alpa-team/alpa/package/alpa/)                         |
| alpa-conf | [![Copr build status](https://copr.fedorainfracloud.org/coprs/alpa-team/alpa/package/python-alpa-conf/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/alpa-team/alpa/package/python-alpa-conf/) |

## Table of contents

<!-- toc -->

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

<!-- tocstop -->

### Requirements

- linux OS
- shell
- at least python3.8
- git

### Installation

From PyPi:

```bash
$ pip install --user pyalpa
```

From Copr:

```bash
$ dnf copr enable alpa-team/alpa
$ dnf install alpa
```

### Usage

#### alpa.yaml config file

Example:

```yaml
---
api_keys:
  - repo:
      name: test-repo
      key: abcd
  - repo:
      name: another-repo
      key: abcd2
  - repo:
      name: yet-another-repo
      key: abcd3
```

### Contributing

TODO
