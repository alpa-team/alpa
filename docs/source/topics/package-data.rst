Files needed to create the package
==================================

Each package needs to specify certain files in order to be built. To build a package, you
need to specify two files in the git root:

* ``metadata.yaml``, which will contain the package metadata for Alpa, such as the targets
  to build the package for, the packager contact, etc.
* spec file


.. _`metadata.yaml`:

Metadata file
-------------

Example:

.. code-block:: yaml

    ---
    autoupdate:
      upstream_pkg_name: pyalpa
      anytia_backend: pypi

      targets_notify_on_fail:
        - fedora-38

    maintainers:
      - user:
          nick: ei
          email: ethernal.ei@inazuma.jp
      - user:
          nick: random_guy
          email: 123@random.r

    targets:
      - fedora-38
      - fedora-rawhide

    arch:
      - x86_64
      - s390x


.. _`autoupdate`:

autoupdate
^^^^^^^^^^

``Optional``

This optional field indicates that you want the package to update itself once in a while
using a special GitHub Action :ref:`automatic_updates`.

Fields:

``upstream_pkg_name``
  Name of package in the upstream, corresponding with correct backend below.

``anytia_backend``
  Backend from where Anytia will monitor new upstream releases. Learn here more about
  :doc:`Release monitoring</topics/release-monitoring>`.

``targets_notify_on_fail``
  A list of targets so important to you so you want to be notified via email about
  their failures when automatic update is happening.

maintainers
^^^^^^^^^^^

``Mandatory``

This field provides necessary information about the maintainers who are responsible for this
particular package.

Fields:

``user``
  This field has two information in it. ``nick`` which is your GitHub nick and ``email`` as
  your email address.

targets
^^^^^^^

``Mandatory``

This field is a list of :ref:`copr_targets`. If field ``target`` is specified in ``.alpa.yaml`` file,
then this field become optional.

arch
^^^^

``Optional``

Specify architectures you want to build for. Defaults to ``x86_64``.


Spec file
---------

The spec file is another very important part of the package creation process. There is
a lot of documentation on the internet for creating a spec file. I recommend you
read `what is a spec file`_.

.. tip::
  Since the creation of the spec file itself is a very critical part of the packaging
  process, about which there is also a lot of documentation written on the
  Internet, it is useful to read and try everything on `rpm-packaging-guide`_
  page except the ``Advanced Topics`` chapter and chapters below.

.. _`what is a spec file`: https://rpm-packaging-guide.github.io/#what-is-a-spec-file
.. _`rpm-packaging-guide`: https://rpm-packaging-guide.github.io/
