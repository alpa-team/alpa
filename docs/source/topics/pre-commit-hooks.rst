pre-commit hooks
================

Alpa provides a couple of pre-commit hooks to check if, for example, all the necessary files
are present for a package to be built and so on. These hooks are mainly used to check for
maintainers if they have forgotten to add some basic important information about the package
and thus try to prevent mistakes due to inattention.

If you want to know more about pre-commit, you can learn about it more `here`_.

.. tip::
  I recommend setting up all the pre-commit hooks (even though it is not mandatory to use
  these), which Alpa provides, to alert you to some basic configuration errors to help
  you save time instead of debugging.

.. _`here`: https://pre-commit.com/

Check necessary files
---------------------

This pre-commit hook check whether you have set up all necessary files that Alpa repo
needs for its functionality. This checks things like if spec file and metadata file is
present.

To enable this hook, put this in your ``pre-commit-config.yaml`` file:

.. code-block:: yaml

  - repo: https://github.com/alpa-team/pre-commit-hooks
    rev: v1.0
    hooks:
      - id: check-necessary-files


Check ``.packit.yaml`` file
---------------------------

This pre-commit hooks check if ``.packit.yaml`` file is present in Alpa repository
since this file is critical for Alpa repository to remain functional. You don't need
to care about this file or configuring it and I recommend not to touch it, because
Alpa generates this file automatically for you. This pre-commit hook exist in case
if you accidentally remove ``.packit.yaml`` when you are doing some changes.
If this is the case, you can re-generate ``.packit.yaml`` file by alpa command
``alpa generate-packit-config``.

To enable this hook, put this in your ``pre-commit-config.yaml`` file:

.. code-block:: yaml

  - repo: https://github.com/alpa-team/pre-commit-hooks
    rev: v1.0
    hooks:
      - id: check-packit-file


``Source0`` must use version macro
----------------------------------

This pre-commit hooks checks whether there is no hardcoded ``Source0`` tag
in your spec file. Please specify version only under the ``Version`` tag in
spec file and use macros to propagate the version to ``Source0`` tag.
This is essential for auto-update to correctly update the package
to update only ``Version`` tag so the change is propagated to
the source from where the upstream source is downloaded.

Correct example of using ``Source0`` tag in spec file:

.. code-block:: spec

    Name:           alpa
    Version:        1.0.0
    Release:        1%{?dist}
    Summary:        Integration tool with Alpa repository

    License:        GPLv3
    URL:            https://github.com/alpa-team/%{name}
    Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

Wrong example of using ``Source0`` tag in spec file:

.. code-block:: spec

    Name:           alpa
    Version:        1.0.0
    Release:        1%{?dist}
    Summary:        Integration tool with Alpa repository

    License:        GPLv3
    URL:            https://github.com/alpa-team/%{name}
    Source0:        %{url}/archive/refs/tags/1.0.0.tar.gz

To enable this hook, put this in your ``pre-commit-config.yaml`` file:

.. code-block:: yaml

  - repo: https://github.com/alpa-team/pre-commit-hooks
    rev: v1.0
    hooks:
      - id: source0-uses-version-macro


Use them all at once
--------------------

If you want to use all pre-commit hooks which Alpa provides, put this in
your ``pre-commit-config.yaml`` file:

.. code-block:: yaml

    - repo: https://github.com/alpa-team/pre-commit-hooks
      rev: v1.0
      hooks:
        - id: check-necessary-files
        - id: check-packit-file
        - id: source0-uses-version-macro
